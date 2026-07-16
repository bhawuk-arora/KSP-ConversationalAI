# backend/app/api/api_v1/endpoints/network.py
import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from neo4j import GraphDatabase

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.schemas.user import UserBase
from app.models.ksp_models import Accused, CaseMaster

router = APIRouter()

# Constables cannot access full network graphs
network_roles = RoleChecker(["Investigator", "Analyst", "Supervisor"])

# Neo4j credentials
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "ksp_neo4j_pass")

def get_neo4j_network(accused_id: int) -> Dict[str, Any]:
    """Cypher query tracing co-accused relationship networks (2-hop radius)."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    try:
        driver.verify_connectivity()
    except Exception as e:
        driver.close()
        raise ConnectionError(f"Neo4j unreachable: {e}")
        
    cypher_query = """
    MATCH (a:Accused {id: $accused_id})
    OPTIONAL MATCH path = (a)-[r1:ACCUSED_IN|CO_ACCUSED_WITH]-(n)-[r2:ACCUSED_IN|CO_ACCUSED_WITH|REPORTED_AT]-(m)
    RETURN path;
    """
    
    nodes_set = {}
    edges_set = {}
    
    with driver.session() as session:
        result = session.run(cypher_query, accused_id=accused_id)
        for record in result:
            path = record.get("path")
            if not path:
                continue
                
            for node in path.nodes:
                labels = list(node.labels)
                label_type = labels[0] if labels else "Accused"
                nid = f"{label_type.lower()}_{node.get('id')}"
                
                # Format label text
                if label_type == "Accused":
                    name = node.get("name") or "Unknown"
                    text = f"{name} (Suspect)"
                elif label_type == "Case":
                    text = f"FIR: {node.get('crime_no')}"
                else:
                    text = node.get("name") or "Station"
                    
                nodes_set[nid] = {
                    "id": nid,
                    "label": text,
                    "type": label_type.lower(),
                }
                
            for rel in path.relationships:
                # Find start and end nodes
                start_labels = list(rel.start_node.labels)
                end_labels = list(rel.end_node.labels)
                start_type = start_labels[0] if start_labels else "Accused"
                end_type = end_labels[0] if end_labels else "Case"
                
                source = f"{start_type.lower()}_{rel.start_node.get('id')}"
                target = f"{end_type.lower()}_{rel.end_node.get('id')}"
                edge_id = f"e_{source}_{target}"
                
                edges_set[edge_id] = {
                    "id": edge_id,
                    "source": source,
                    "target": target,
                    "label": rel.type
                }
                
    driver.close()
    
    # If target suspect exists but has no links
    if not nodes_set:
        return {"nodes": [], "edges": []}
        
    return {
        "nodes": list(nodes_set.values()),
        "edges": list(edges_set.values())
    }

def get_relational_fallback_network(accused_id: int, db: Session) -> Dict[str, Any]:
    """
    SQL fallback compiling case relationships when Neo4j is offline.
    Traces: Accused -> CaseMaster -> Co-Accused on the same CaseMaster.
    """
    nodes = []
    edges = []
    
    # Fetch target suspect
    target = db.query(Accused).filter(Accused.AccusedMasterID == accused_id).first()
    if not target:
        return {"nodes": [], "edges": []}
        
    t_node_id = f"accused_{target.AccusedMasterID}"
    nodes.append({
        "id": t_node_id,
        "label": f"{target.AccusedName} (Target)",
        "type": "accused"
    })
    
    # Find all cases this accused is linked to
    cases = db.query(CaseMaster).join(Accused, CaseMaster.CaseMasterID == Accused.CaseMasterID)\
              .filter(Accused.AccusedMasterID == accused_id).limit(10).all()
              
    for case in cases:
        c_node_id = f"case_{case.CaseMasterID}"
        nodes.append({
            "id": c_node_id,
            "label": f"FIR: {case.CrimeNo}",
            "type": "case"
        })
        edges.append({
            "id": f"e_{t_node_id}_{c_node_id}",
            "source": t_node_id,
            "target": c_node_id,
            "label": "ACCUSED_IN"
        })
        
        # Find co-accused on this case
        co_suspects = db.query(Accused).filter(
            Accused.CaseMasterID == case.CaseMasterID, 
            Accused.AccusedMasterID != accused_id
        ).limit(5).all()
        
        for co in co_suspects:
            co_node_id = f"accused_{co.AccusedMasterID}"
            # Avoid duplicate nodes
            if not any(n["id"] == co_node_id for n in nodes):
                nodes.append({
                    "id": co_node_id,
                    "label": f"{co.AccusedName} (Co-Accused)",
                    "type": "accused"
                })
            
            # ACCUSED_IN link
            edges.append({
                "id": f"e_{co_node_id}_{c_node_id}",
                "source": co_node_id,
                "target": c_node_id,
                "label": "ACCUSED_IN"
            })
            
            # CO_ACCUSED_WITH direct links
            edges.append({
                "id": f"e_{t_node_id}_{co_node_id}",
                "source": t_node_id,
                "target": co_node_id,
                "label": "CO_ACCUSED_WITH"
            })
            
    return {"nodes": nodes, "edges": edges}

@router.get("/suspect/{accused_id}", response_model=Dict[str, Any])
def trace_suspect_network(
    accused_id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(network_roles),
):
    """
    Traces relationship paths and co-offenders up to 2-hops.
    Leverages Neo4j graph queries, falling back gracefully to PostgreSQL full relationships.
    """
    try:
        # Try Cypher query on Neo4j
        result = get_neo4j_network(accused_id)
        if result and result.get("nodes"):
            return result
    except Exception as e:
        print(f"[NEO4J OFFLINE FALLBACK] {e}")
    
    # Run Postgres SQL compilation fallback
    return get_relational_fallback_network(accused_id, db)
