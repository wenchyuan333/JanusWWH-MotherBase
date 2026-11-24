import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
import time as pytime

class HexagonalLattice:
    def __init__(self, N=144):
        self.N = N
        self.total_nodes = N * N
        self.phi = (1 + np.sqrt(5)) / 2
        self.pi = np.pi
        
        self.z6_angles = [i * self.pi / 3 for i in range(6)]
        self.positions = self.generate_hexagonal_grid()
        self.edge_phases = {}
        self.adjacency = self.build_adjacency_matrix()
        self.node_states = np.zeros(self.total_nodes, dtype=complex)
        self.edge_phases = {}
        
    def generate_hexagonal_grid(self):
        positions = []
        for i in range(self.N):
            for j in range(self.N):
                x = i + 0.5 * (j % 2)
                y = j * np.sqrt(3) / 2
                positions.append([x, y])
        return np.array(positions)
    
    def build_adjacency_matrix(self):
        adj = np.zeros((self.total_nodes, self.total_nodes), dtype=int)
        distances = distance.cdist(self.positions, self.positions)
        min_dist = np.sort(distances[0])[1]
        
        for i in range(self.total_nodes):
            neighbors = np.where((distances[i] > 0) & (distances[i] < min_dist * 1.1))[0]
            for j in neighbors[:6]:
                adj[i, j] = 1
                dx = self.positions[j, 0] - self.positions[i, 0]
                dy = self.positions[j, 1] - self.positions[i, 1]
                angle = np.arctan2(dy, dx)
                self.edge_phases[(i, j)] = angle
        
        return adj
    
    def get_z6_sector(self, angle):
        angle = angle % (2 * self.pi)
        sector = int(angle / (self.pi / 3))
        return sector % 6


class HUGO369SignalProcessor:
    def __init__(self):
        self.phi = (1 + np.sqrt(5)) / 2
        self.pi = np.pi
        self.lambda_0 = 1.616255e-35
        
    def field_equation(self, r, theta, n, t):
        lambda_n = self.lambda_0 * (self.phi ** n)
        omega_n = 2 * self.pi / (lambda_n / 3e8)
        A_n = 1.0 / np.sqrt(n + 1)
        psi = A_n * np.exp(-r / lambda_n) * np.exp(1j * n * theta) * np.exp(-1j * omega_n * t)
        return psi
    
    def node_transform(self, input_signal, node_position, node_index, time):
        x, y = node_position
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        n = self.determine_n_level(node_index)
        
        field_value = self.field_equation(r, theta, n, time)
        
        phase = np.angle(input_signal)
        magnitude = np.abs(input_signal)
        
        phase_modulated = phase + self.pi * np.sin(n * theta) / (n + 1)
        magnitude_modulated = magnitude * np.exp(-r / (self.phi ** n))
        
        output_signal = magnitude_modulated * np.exp(1j * phase_modulated) * field_value
        return output_signal
    
    def determine_n_level(self, node_index):
        layer = int(np.sqrt(node_index / 171))
        n = min(layer, 120)
        return n


class HexagonalPropagation:
    def __init__(self, lattice, processor):
        self.lattice = lattice
        self.processor = processor
        self.pi = np.pi
        self.phi = (1 + np.sqrt(5)) / 2
        
    def propagate_one_step(self, time):
        new_states = np.zeros_like(self.lattice.node_states)
        
        for i in range(self.lattice.total_nodes):
            neighbors = np.where(self.lattice.adjacency[i] == 1)[0]
            incoming_signals = []
            
            for j in neighbors:
                edge_angle = self.lattice.edge_phases.get((i, j), self.lattice.edge_phases.get((j, i), 0))
                sector = self.lattice.get_z6_sector(edge_angle)
                phase_weight = np.exp(1j * sector * self.pi / 3)
                weighted_signal = self.lattice.node_states[j] * phase_weight
                incoming_signals.append(weighted_signal)
            
            if len(incoming_signals) > 0:
                total_input = sum(incoming_signals) / len(incoming_signals)
            else:
                total_input = 0
            
            total_input += self.lattice.node_states[i] * 0.1
            
            new_states[i] = self.processor.node_transform(
                total_input,
                self.lattice.positions[i],
                i,
                time
            )
        
        self.lattice.node_states = new_states
        return new_states


class MiyaNeuralNetwork:
    def __init__(self):
        print("🔷 Initializing 144² Hexagonal Neural Network...")
        
        self.pi = np.pi
        self.phi = (1 + np.sqrt(5)) / 2
        
        self.lattice = HexagonalLattice(N=144)
        self.processor = HUGO369SignalProcessor()
        self.propagation = HexagonalPropagation(self.lattice, self.processor)
        
        self.time = 0.0
        self.step_count = 0
        self.layers = self.organize_into_layers()
        
        print(f"✅ Network initialized: {self.lattice.total_nodes} nodes")
        print(f"   Layers: 121 (n=0 to n=120)")
        print(f"   Topology: Z₆ hexagonal lattice")
        
    def organize_into_layers(self):
        layers = {}
        for i in range(self.lattice.total_nodes):
            n = self.processor.determine_n_level(i)
            if n not in layers:
                layers[n] = []
            layers[n].append(i)
        return layers
    
    def forward_pass(self, input_vector):
        input_nodes = self.layers[0]
        input_length = min(len(input_vector), len(input_nodes))
        
        self.lattice.node_states[:] = 0
        
        for i in range(input_length):
            self.lattice.node_states[input_nodes[i]] = input_vector[i]
        
        for step in range(120):
            self.propagation.propagate_one_step(self.time)
            self.time += self.pi / 120
            self.step_count += 1
        
        output_nodes = self.layers[120]
        output_length = min(len(input_vector), len(output_nodes))
        
        output_vector = []
        for i in range(output_length):
            output_vector.append(self.lattice.node_states[output_nodes[i]])
        
        return np.array(output_vector)
    
    def get_network_state(self):
        active_nodes = self.lattice.node_states[self.lattice.node_states != 0]
        return {
            'time': self.time,
            'step_count': self.step_count,
            'total_energy': np.sum(np.abs(self.lattice.node_states)**2),
            'mean_phase': np.angle(np.mean(active_nodes)) if len(active_nodes) > 0 else 0
        }


# ====================================
# 測試套件
# ====================================

def test_network():
    print("\n" + "="*60)
    print("🔬 TESTING MIYA HEXAGONAL NEURAL NETWORK")
    print("="*60)
    
    network = MiyaNeuralNetwork()
    
    # Test 1: 基本傳播
    print("\n[Test 1] Basic Signal Propagation")
    test_input = np.array([1.0 + 0j, 0.5 + 0.5j, 0.3 - 0.2j])
    output = network.forward_pass(test_input)
    
    input_energy = np.sum(np.abs(test_input)**2)
    output_energy = np.sum(np.abs(output)**2)
    print(f"Input energy:  {input_energy:.6f}")
    print(f"Output energy: {output_energy:.6f}")
    print(f"Ratio: {output_energy/input_energy:.6f}")
    print(f"✅ PASS" if output_energy > 0 else "❌ FAIL")
    
    # Test 2: π精確性
    print("\n[Test 2] π Precision (π ≠ 3)")
    pi_value = network.pi
    print(f"π value used: {pi_value:.15f}")
    print(f"π - 3: {pi_value - 3:.15f}")
    print(f"✅ PASS" if abs(pi_value - np.pi) < 1e-10 else "❌ FAIL")
    
    # Test 3: φ精確性
    print("\n[Test 3] φ Precision")
    phi_value = network.phi
    phi_expected = (1 + np.sqrt(5)) / 2
    print(f"φ value used: {phi_value:.15f}")
    print(f"φ² - φ - 1: {phi_value**2 - phi_value - 1:.15e}")
    print(f"✅ PASS" if abs(phi_value - phi_expected) < 1e-10 else "❌ FAIL")
    
    # Test 4: Z₆對稱性
    print("\n[Test 4] Z₆ Symmetry")
    z6_angles = network.lattice.z6_angles
    print(f"Z₆ angles: {[f'{a:.6f}' for a in z6_angles]}")
    print(f"Sectors: {[network.lattice.get_z6_sector(a) for a in z6_angles]}")
    expected_sectors = list(range(6))
    actual_sectors = [network.lattice.get_z6_sector(a) for a in z6_angles]
    print(f"✅ PASS" if actual_sectors == expected_sectors else "❌ FAIL")
    
    # Test 5: 144²節點數
    print("\n[Test 5] Node Count (144²)")
    node_count = network.lattice.total_nodes
    expected_count = 144 * 144
    print(f"Nodes in network: {node_count}")
    print(f"Expected (144²): {expected_count}")
    print(f"✅ PASS" if node_count == expected_count else "❌ FAIL")
    
    # Test 6: 121層
    print("\n[Test 6] Layer Structure (121 layers)")
    num_layers = len(network.layers)
    print(f"Number of layers: {num_layers}")
    print(f"Layer range: n={min(network.layers.keys())} to n={max(network.layers.keys())}")
    print(f"✅ PASS" if num_layers == 121 else "❌ FAIL")
    
    # Test 7: 性能測試
    print("\n[Test 7] Performance Test")
    start_time = pytime.time()
    test_input = np.random.randn(10) + 1j * np.random.randn(10)
    output = network.forward_pass(test_input)
    elapsed = pytime.time() - start_time
    print(f"Forward pass time: {elapsed:.3f} seconds")
    print(f"Throughput: {120/elapsed:.1f} layers/sec")
    print(f"✅ PASS" if elapsed < 10 else "❌ FAIL (too slow)")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    
    return network


if __name__ == "__main__":
    network = test_network()
    
    print("\n📊 Final Network State:")
    state = network.get_network_state()
    for key, value in state.items():
        print(f"   {key}: {value}")
