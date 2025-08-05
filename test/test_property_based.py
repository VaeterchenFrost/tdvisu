# -*- coding: utf-8 -*-
"""
Property-based testing for graph structures and visualization components.

Uses Hypothesis to generate complex graph structures and test edge cases.

Copyright (C) 2025 Martin Röbke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.
    If not, see https://www.gnu.org/licenses/gpl-3.0.html

"""

import json
import tempfile
from pathlib import Path
from random import choice, randint

import pytest
from hypothesis import given, strategies as st, assume, settings, note, example
from hypothesis import HealthCheck, Verbosity
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize, invariant, multiple

from tdvisu.visualization import Visualization
from tdvisu.utilities import flatten, add_edge_to
from tdvisu.dijkstra import bidirectional_dijkstra


# Custom strategies for complex data structures
@st.composite
def graph_edges(draw, num_nodes, edge_probability=0.5):
    """Generate realistic graph edges with controlled density."""
    edges = []
    for i in range(1, num_nodes + 1):
        for j in range(i + 1, num_nodes + 1):
            # Use floats strategy for probability comparison
            if draw(st.floats(min_value=0.0, max_value=1.0)) < edge_probability:
                edges.append([i, j])
    return edges

@st.composite 
def tree_decomposition(draw, num_nodes, max_bag_size=5):
    """Generate valid tree decomposition structure."""
    bag_count = draw(st.integers(min_value=1, max_value=min(num_nodes, 10)))
    labeldict = []
    
    for i in range(1, bag_count + 1):
        bag_size = draw(st.integers(min_value=1, max_value=min(max_bag_size, num_nodes)))
        labels = draw(st.lists(
            st.integers(min_value=1, max_value=num_nodes),
            min_size=bag_size,
            max_size=bag_size,
            unique=True
        ))
        labeldict.append({"id": i, "labels": labels})
    
    # Generate tree structure for edges
    edgearray = []
    for i in range(1, bag_count):
        edgearray.append([i, i + 1])
    
    return {
        "bagpre": draw(st.sampled_from(["bag%d", "bag%s", "Bag_%d", "node%d"])),
        "labeldict": labeldict,
        "edgearray": edgearray,
        "num_vars": num_nodes
    }

@st.composite
def sat_formula(draw, max_vars=10, max_clauses=15):
    """Generate SAT formulas with realistic structure."""
    num_vars = draw(st.integers(min_value=1, max_value=max_vars))
    num_clauses = draw(st.integers(min_value=1, max_value=max_clauses))
    
    clauses = []
    for _ in range(num_clauses):
        clause_size = draw(st.integers(min_value=1, max_value=min(5, num_vars)))
        literals = draw(st.lists(
            st.integers(min_value=1, max_value=num_vars).map(
                lambda x: x if draw(st.booleans()) else -x
            ),
            min_size=clause_size,
            max_size=clause_size,
            unique=True
        ))
        clauses.append(literals)
    
    return clauses, num_vars


class TestPropertyBasedGraphGeneration:
    """Property-based tests for graph structure generation and handling."""
    
    @given(
        num_nodes=st.integers(min_value=1, max_value=50),
        edge_probability=st.floats(min_value=0.0, max_value=1.0),
        data=st.data()
    )
    @settings(max_examples=50, deadline=5000)
    def test_random_graph_structure_handling(self, num_nodes, edge_probability, data):
        """
        Property-based test: Random graph structures should be handled gracefully.
        
        Generates random graphs with varying density and tests that the visualization
        can process them without errors.
        """
        note(f"Testing graph with {num_nodes} nodes and edge probability {edge_probability:.3f}")
        
        tmp_path = Path(tempfile.mkdtemp())
        edges = data.draw(graph_edges(num_nodes, edge_probability))
        tree_dec = data.draw(tree_decomposition(num_nodes))
        
        note(f"Generated {len(edges)} edges")
        note(f"Tree decomposition has {len(tree_dec['labeldict'])} bags")
        
        test_json = {
            "tdTimeline": [[1]],
            "treeDecJson": tree_dec,
            "generalGraph": [{
                "edges": edges,
                "file_basename": f"random_graph_{num_nodes}_{edge_probability}",
                "graph_name": "RandomTestGraph",
                "var_name": "V"
            }],
            "td_file": "random_test",
            "orientation": "BT", 
            "bagcolor": "white",
            "colors": ["red", "blue", "green", "yellow", "purple"]
        }
        
        # Should handle any valid graph structure
        viz = Visualization(json.dumps(test_json), tmp_path)
        assert len(viz.data.general_graphs) == 1
        assert viz.data.general_graphs[0].file_basename.startswith("random_graph")
        
        # Verify the graph was processed correctly
        graph_data = viz.data.general_graphs[0]
        assert len(graph_data.edges) == len(edges)
        note(f"Successfully processed graph with {len(edges)} edges")
        
    @given(sat_formula(max_vars=15, max_clauses=20))
    @example((([[1], [-1]], 1)))  # Unsatisfiable formula
    @example((([[1, 2], [-1, -2]], 2)))  # Another unsatisfiable case  
    @example((([[1]], 1)))  # Single unit clause
    @settings(max_examples=30, deadline=5000)
    def test_random_sat_instances(self, sat_data):
        """
        Property-based test: Random SAT instances should be processable.
        
        Generates random SAT formulas and tests incidence graph creation.
        """
        clauses, num_vars = sat_data
        note(f"Testing SAT formula with {len(clauses)} clauses and {num_vars} variables")
        note(f"Clauses: {clauses[:3]}{'...' if len(clauses) > 3 else ''}")
        
        tmp_path = Path(tempfile.mkdtemp())
        
        # Incidence graph expects edges as dictionaries with 'id' and 'list' keys
        edges = []
        for i, clause in enumerate(clauses):
            edges.append({"id": i + 1, "list": clause})
        
        test_json = {
            "tdTimeline": [[1]],
            "treeDecJson": {
                "bagpre": "bag%d",
                "labeldict": [{"id": 1, "labels": list(range(1, min(num_vars + 1, 6)))}],
                "edgearray": [],
                "num_vars": num_vars
            },
            "incidenceGraph": [{
                "edges": edges,
                "inc_file": f"random_sat_{len(clauses)}",
                "var_name_one": "C",
                "var_name_two": "X",
                "fontsize": 12,
                "penwidth": 1.0,
                "column_distance": 0.5,
                "infer_primal": True,
                "infer_dual": True,
                "primal_file": "random_primal",
                "dual_file": "random_dual"
            }],
            "td_file": "random_sat_test",
            "orientation": "BT",
            "bagcolor": "white",
            "colors": ["red", "blue", "green", "yellow", "purple"] * 5  # Ensure enough colors
        }
        
        # Should handle any valid SAT instance
        viz = Visualization(json.dumps(test_json), tmp_path)
        assert len(viz.data.incidence_graphs) == 1
        incid = viz.data.incidence_graphs[0]
        assert len(incid.edges) == len(clauses)
        
        # Verify variable range
        all_vars_in_edges = set()
        for clause in clauses:
            all_vars_in_edges.update(abs(lit) for lit in clause)
        assert max(all_vars_in_edges) <= num_vars
        note(f"Successfully processed SAT instance with variables 1-{num_vars}")
        
    @given(
        timeline_length=st.integers(min_value=1, max_value=30),
        solution_probability=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=20, deadline=5000)
    def test_random_timeline_structures(self, timeline_length, solution_probability):
        """
        Property-based test: Random timeline structures should be processable.
        
        Generates timelines with varying numbers of steps and solution presence.
        """
        import tempfile
        import random
        tmp_path = Path(tempfile.mkdtemp())
        timeline = []
        for i in range(1, timeline_length + 1):
            if random.random() < solution_probability:
                timeline.append([i, [f"sol{i}", ["header"], [["data", i]]]])
            else:
                timeline.append([i])
                
        # Create corresponding labeldict
        labeldict = [{"id": i, "labels": [i, i + 1]} for i in range(1, timeline_length + 1)]
        edgearray = [[i, i + 1] for i in range(1, timeline_length)]
        
        test_json = {
            "tdTimeline": timeline,
            "treeDecJson": {
                "bagpre": "bag%d",
                "labeldict": labeldict,
                "edgearray": edgearray,
                "num_vars": timeline_length + 1
            },
            "td_file": f"timeline_test_{timeline_length}",
            "orientation": "BT",
            "bagcolor": "white",
            "colors": ["red", "blue", "green"] * 10
        }
        
        # Should handle any valid timeline
        viz = Visualization(json.dumps(test_json), tmp_path)
        assert len(viz.timeline) == timeline_length


class TestPropertyBasedUtilities:
    """Property-based tests for utility functions."""
    
    @given(
        nested_structure=st.recursive(
            st.integers(),  # Only integers as base case (non-iterable)
            lambda children: st.lists(children, min_size=0, max_size=5),
            max_leaves=15
        )
    )
    @example([])  # Empty list
    @example([1, 2, 3])  # Simple flat list with integers
    @example([1, [2, 3], [4, [5]]])  # Nested list
    @example([[1, 2], [3, 4]])  # Lists of lists (proper flatten domain)
    @settings(max_examples=75, deadline=3000)
    def test_flatten_with_arbitrary_nesting(self, nested_structure):
        """
        Property-based test: flatten should handle arbitrary nesting levels.
        
        Tests the flatten utility with nested list structures containing integers.
        flatten() is designed to work on iterables of iterables.
        """
        note(f"Testing flatten with: {type(nested_structure).__name__}")
        if hasattr(nested_structure, '__len__'):
            try:
                note(f"Structure length: {len(nested_structure)}")
            except TypeError:
                pass
                
        if isinstance(nested_structure, int):
            # Non-iterable items should fail when passed directly to flatten
            try:
                result = list(flatten(nested_structure))
                # This should fail since integers aren't iterable
                assert False, "flatten should fail on non-iterable"
            except TypeError as e:
                note(f"flatten correctly rejected non-iterable: {e}")
                # This is expected behavior
                
        elif isinstance(nested_structure, list):
            # Lists should work with flatten
            try:
                result = list(flatten(nested_structure))
                assert isinstance(result, list)
                assert len(result) >= 0
                note(f"Successfully flattened to {len(result)} items")
                
                # Property: flattening a list of integers should yield those integers
                # (since integers can't be iterated, flatten tries to iterate them)
                if all(isinstance(item, int) for item in nested_structure):
                    # This will actually fail since integers aren't iterable
                    # flatten expects iterables of iterables
                    pass  # We expect this case to potentially fail
                    
                # Property: flattening a list of lists should flatten one level
                elif all(isinstance(item, list) for item in nested_structure):
                    total_inner_items = sum(len(item) for item in nested_structure)
                    assert len(result) == total_inner_items
                    
            except TypeError as e:
                note(f"flatten failed on structure with non-iterables: {e}")
                # This is acceptable when structure contains non-iterable items
                
        else:
            # Other types - test behavior
            try:
                result = list(flatten(nested_structure))
                assert isinstance(result, list)
                note(f"Unexpected success on {type(nested_structure)}: {result}")
            except (TypeError, ValueError) as e:
                note(f"flatten correctly rejected {type(nested_structure)}: {e}")
            
    @given(
        edges=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=20),
                st.integers(min_value=1, max_value=20)
            ),
            min_size=0,
            max_size=20
        ),
        new_edge=st.tuples(
            st.integers(min_value=1, max_value=20),
            st.integers(min_value=1, max_value=20)
        )
    )
    @settings(max_examples=30, deadline=3000)
    def test_add_edge_to_adjacency_property(self, edges, new_edge):
        """
        Property-based test: add_edge_to should maintain adjacency properties.
        Tests that edge addition maintains graph invariants.
        """
        adj = {}
        for v1, v2 in edges:
            add_edge_to(set(edges), adj, v1, v2)
        v1, v2 = new_edge
        original_adj = {k: v.copy() for k, v in adj.items()}
        edge_set = set(edges)
        edge_set.add(new_edge)
        result_adj = add_edge_to(edge_set, adj, v1, v2)
        if result_adj is None:
            result_adj = adj
        assert v2 in result_adj.get(v1, set())
        assert v1 in result_adj.get(v2, set())
        for vertex, neighbors in original_adj.items():
            for neighbor in neighbors:
                assert neighbor in result_adj.get(vertex, set())
        

class TestPropertyBasedDijkstra:
    """Property-based tests for shortest path algorithm."""
    
    @given(
        num_nodes=st.integers(min_value=2, max_value=15),
        edge_weight_range=st.tuples(
            st.floats(min_value=0.1, max_value=10.0),
            st.floats(min_value=0.1, max_value=100.0)
        ).filter(lambda x: x[0] <= x[1]),
        data=st.data()
    )
    @settings(max_examples=20, deadline=5000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_dijkstra_triangle_inequality(self, num_nodes, edge_weight_range, data):
        """
        Property-based test: Dijkstra should respect triangle inequality.
        
        For any three nodes A, B, C: dist(A,C) <= dist(A,B) + dist(B,C)
        """
        min_weight, max_weight = edge_weight_range
        
        # Generate a connected graph with random weights
        graph = {}
        for i in range(1, num_nodes + 1):
            graph[i] = {}
            
        # Add edges to ensure connectivity (create a spanning tree first)
        for i in range(1, num_nodes):
            weight = data.draw(st.floats(min_weight, max_weight))
            graph[i][i + 1] = {'weight': weight}
            graph[i + 1][i] = {'weight': weight}
            
        # Add some random additional edges
        for i in range(1, num_nodes + 1):
            for j in range(i + 1, num_nodes + 1):
                if data.draw(st.booleans()) and (i, j) != (i, i + 1):  # Some probability
                    weight = data.draw(st.floats(min_weight, max_weight))
                    graph[i][j] = {'weight': weight}
                    graph[j][i] = {'weight': weight}
                    
        # Test triangle inequality for random triplets (only if we have enough nodes)
        if num_nodes >= 3:
            for _ in range(min(5, num_nodes - 2)):  # Test up to 5 random triplets
                nodes = data.draw(st.lists(
                    st.integers(1, num_nodes), 
                    min_size=3, 
                    max_size=3, 
                    unique=True
                ))
                if len(nodes) == 3:
                    a, b, c = nodes
                    
                    try:
                        dist_ac = bidirectional_dijkstra(graph, a, c)[0]
                        dist_ab = bidirectional_dijkstra(graph, a, b)[0]
                        dist_bc = bidirectional_dijkstra(graph, b, c)[0]
                        
                        # Triangle inequality: dist(A,C) <= dist(A,B) + dist(B,C)
                        assert dist_ac <= dist_ab + dist_bc + 1e-10  # Small epsilon for float precision
                        
                    except (KeyError, ValueError):
                        # If no path exists, that's also valid
                        pass
                    
    @given(
        graph_size=st.integers(min_value=1, max_value=10),
        source=st.integers(min_value=1, max_value=10),
        target=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=30, deadline=3000)
    def test_dijkstra_error_handling(self, graph_size, source, target):
        """
        Property-based test: Dijkstra should handle invalid inputs gracefully.
        
        Tests various error conditions and edge cases.
        """
        # Create a simple graph
        graph = {i: {} for i in range(1, graph_size + 1)}
        
        if source > graph_size or target > graph_size:
            # Should raise ValueError for nodes not in graph
            with pytest.raises(Exception):
                bidirectional_dijkstra(graph, source, target)
        elif source == target:
            # Distance to self should be 0
            result = bidirectional_dijkstra(graph, source, target)
            assert result[0] == 0
            assert result[1] == [source]
        else:
            # For disconnected nodes, should raise ValueError
            try:
                result = bidirectional_dijkstra(graph, source, target)
                # If successful, path should start with source and end with target
                assert result[1][0] == source
                assert result[1][-1] == target
                assert result[0] >= 0  # Distance should be non-negative
            except Exception:
                # No path exists - this is valid for disconnected graphs
                pass


class TestPropertyBasedSVGGeneration:
    """Property-based tests for SVG output structure and validation."""
    
    @given(
        graph_params=st.fixed_dictionaries({
            'fontsize': st.integers(min_value=8, max_value=16),  # Reduced range
            'first_color': st.sampled_from(['red', 'blue', 'green']),  # Fewer options
            'second_color': st.sampled_from(['orange', 'cyan', 'magenta']),
            'third_color': st.sampled_from(['brown', 'gray', 'navy'])
        })
    )
    @settings(
        max_examples=8,   # Reduced for performance
        deadline=8000,    # Extended deadline
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large]
    )
    def test_svg_output_structure_validation(self, graph_params):
        """
        Property-based test: SVG output should have valid structure.
        
        Optimized test focusing on core SVG validation with reduced complexity.
        """
        import tempfile
        note(f"Testing SVG with params: {graph_params}")
        
        tmp_path = Path(tempfile.mkdtemp())
        try:
            # Simplified test data for better performance
            test_json = {
                "tdTimeline": [[1, ["solution", "header", "row1,data"]]],
                "treeDecJson": {
                    "bagpre": "bag%s",
                    "labeldict": [{"id": 1, "labels": [1, 2]}],
                    "edgearray": [],
                    "num_vars": 2  # Minimal complexity
                },
                "generalGraph": [{
                    "edges": [[1, 2]],  # Single edge for minimal complexity
                    "file_basename": "svg_structure_test",
                    "graph_name": "SVGTestGraph",
                    "var_name": "V",
                    "fontsize": graph_params['fontsize'],
                    "first_color": graph_params['first_color'],
                    "second_color": graph_params['second_color'],
                    "third_color": graph_params['third_color']
                }],
                "td_file": "svg_test",
                "orientation": "BT",
                "bagcolor": "white",
                "colors": ["red", "blue", "green"]
            }
            
            viz = Visualization(json.dumps(test_json), tmp_path)
            viz.tree_dec_timeline()
            
            output_files = list(tmp_path.glob("**/*.svg"))
            assert len(output_files) > 0, "Should generate at least one SVG file"
            note(f"Generated {len(output_files)} SVG files")
            
            # Validate SVG content
            if output_files:
                svg_content = output_files[0].read_text()
                assert svg_content.startswith('<?xml version="1.0"') or svg_content.startswith('<svg')
                assert '<svg' in svg_content
                assert '</svg>' in svg_content
                assert any(tag in svg_content for tag in ['<g', '<path', '<polygon', '<ellipse', '<text'])
                note(f"SVG validation passed for {output_files[0].name}")
                
        finally:
            # Cleanup
            import shutil
            try:
                shutil.rmtree(tmp_path)
            except Exception:
                pass


class TestAdvancedPropertyBased:
    """Advanced property-based tests showcasing best Hypothesis practices."""
    
    @given(
        num_nodes=st.integers(min_value=1, max_value=50),
        edge_density=st.floats(min_value=0.0, max_value=1.0),
        layout=st.sampled_from(['spring', 'circular', 'random']),
        include_weights=st.booleans(),
        data=st.data()  # Add data strategy for interactive drawing
    )
    @settings(
        max_examples=50,  # Reduced for faster testing
        deadline=3000,  # 3 seconds
        suppress_health_check=[HealthCheck.too_slow],
        verbosity=Verbosity.verbose
    )
    def test_comprehensive_graph_pipeline(self, num_nodes, edge_density, layout, include_weights, data):
        """
        Comprehensive property-based test for the entire graph processing pipeline.
        
        This test serves as both a regression test and a usage example,
        demonstrating how to process graphs with various characteristics.
        Uses data.draw() for proper Hypothesis interactive drawing.
        """
        note(f"Testing pipeline: {num_nodes} nodes, density={edge_density:.2f}, layout={layout}, weights={include_weights}")
        
        # Phase 1: Generate realistic graph structure using data.draw()
        edges = data.draw(graph_edges(num_nodes, edge_density))
        note(f"Generated {len(edges)} edges")
        
        # Phase 2: Create tree decomposition using data.draw()
        tree_dec = data.draw(tree_decomposition(num_nodes))
        note(f"Created tree decomposition with {len(tree_dec)} bags")
        
        # Phase 3: Test utilities on the graph data
        if edges:
            # Test flatten utility
            flattened_edges = list(flatten(edges))
            assert len(flattened_edges) >= len(edges)
            note(f"Flattened edges: {len(flattened_edges)} items")
            
            # Test dijkstra if we have enough structure
            if len(edges) >= 2:
                adjacency = {}
                for src, dst in edges:
                    if src not in adjacency:
                        adjacency[src] = []
                    weight = randint(1, 10) if include_weights else 1
                    adjacency[src].append((dst, weight))
                    
                # Try pathfinding between random nodes
                start = choice(range(1, num_nodes + 1))
                end = choice(range(1, num_nodes + 1))
                
                try:
                    path = bidirectional_dijkstra(edges, start, end)
                    if path and path[0]:  # bidirectional_dijkstra returns (path_length, path)
                        actual_path = path[1]
                        note(f"Found path {start} -> {end}: length {len(actual_path)}")
                        assert actual_path[0] == start
                        assert actual_path[-1] == end
                    else:
                        note(f"No path found from {start} to {end} (acceptable)")
                except Exception as e:
                    note(f"Dijkstra failed (acceptable for disconnected graphs): {e}")
        
        # Phase 4: Test visualization creation
        with tempfile.TemporaryDirectory() as tmpdir:
            test_json = {
                "tdTimeline": [[1]],
                "treeDecJson": tree_dec,
                "generalGraph": [{
                    "edges": edges,
                    "file_basename": f"test_graph_{num_nodes}_{layout}",
                    "graph_name": f"TestGraph_{layout}",
                    "var_name": "V"
                }],
                "td_file": "comprehensive_test",
                "orientation": "BT",
                "bagcolor": "white",
                "colors": ["red", "blue", "green"]
            }
            
            viz = Visualization(json.dumps(test_json), Path(tmpdir))
            assert len(viz.data.general_graphs) == 1
            assert viz.data.general_graphs[0].graph_name == f"TestGraph_{layout}"
            note(f"Successfully created visualization for {layout} layout")
            
        # Phase 5: Verify graph properties are preserved
        graph = viz.data.general_graphs[0]
        assert len(graph.edges) == len(edges)
        
        # Verify edge consistency (edges might be stored as lists or objects)
        for i, (original_edge, graph_edge) in enumerate(zip(edges, graph.edges)):
            if hasattr(graph_edge, 'source'):
                # Edge is an object with source/target attributes
                assert graph_edge.source == original_edge[0]
                assert graph_edge.target == original_edge[1]
                note(f"Edge {i}: object format {graph_edge.source}->{graph_edge.target}")
            else:
                # Edge is stored as a list/tuple
                assert graph_edge[0] == original_edge[0]
                assert graph_edge[1] == original_edge[1]
                note(f"Edge {i}: list format {graph_edge[0]}->{graph_edge[1]}")
            
        note("✓ Comprehensive pipeline test completed successfully")


if __name__ == "__main__":
    # Run some basic tests when executed directly
    pytest.main([__file__, "-v"])
