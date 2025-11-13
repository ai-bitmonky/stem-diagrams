from core.property_graph import (
    PropertyGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType,
)


def test_property_graph_serialization_roundtrip(tmp_path):
    pg = PropertyGraph()
    battery = GraphNode(id="battery_1", type=NodeType.OBJECT, label="Battery")
    voltage = GraphNode(
        id="voltage_1",
        type=NodeType.QUANTITY,
        label="Voltage",
        properties={"unit": "V", "value": 12},
    )
    pg.add_node(battery)
    pg.add_node(voltage)
    pg.add_edge(
        GraphEdge(
            source="battery_1",
            target="voltage_1",
            type=EdgeType.HAS_VALUE,
            label="has_voltage",
        )
    )

    output_path = tmp_path / "graph.json"
    pg.to_json(str(output_path))
    assert output_path.exists()

    loaded = PropertyGraph.from_json(str(output_path))
    assert len(loaded.get_all_nodes()) == 2
    assert len(loaded.get_edges()) == 1
    restored_voltage = loaded.get_node("voltage_1")
    assert restored_voltage.properties["unit"] == "V"


def test_property_graph_gap_queries_and_metadata_merge():
    pg = PropertyGraph()
    dielectric = GraphNode(id="d1", type=NodeType.OBJECT, label="Dielectric layer")
    quantity = GraphNode(
        id="q1", type=NodeType.QUANTITY, label="Permittivity", properties={}
    )
    pg.add_node(dielectric)
    pg.add_node(quantity)

    missing_units = pg.find_nodes_missing_property("unit", node_type=NodeType.QUANTITY)
    assert [node.id for node in missing_units] == ["q1"]

    dielectric_missing = pg.find_nodes_missing_property(
        "kappa", label_contains="dielectric"
    )
    assert dielectric_missing and dielectric_missing[0].id == "d1"

    pg.merge_node_metadata("d1", {"ontologies": [{"namespace": "physh", "uri": "x"}]})
    pg.merge_node_metadata("d1", {"ontologies": [{"namespace": "physh", "uri": "x"}]})
    metadata = pg.get_node("d1").metadata
    assert len(metadata["ontologies"]) == 1
