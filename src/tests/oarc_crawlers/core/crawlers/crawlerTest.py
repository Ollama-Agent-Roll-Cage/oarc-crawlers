"""
ArXiv Crawler Examples with Network Visualization

This script demonstrates:
1. Crawling papers and their citation networks
2. Handling different ArXiv URL formats
3. Saving data in Parquet format
4. Visualizing citation networks using PyVis
5. Interactive GUI using PyQt6
"""

import asyncio
from pathlib import Path
import sys
from typing import List, Optional, Union
import json

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QLineEdit, QSpinBox, QLabel, QTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal
from pyvis.network import Network

from oarc_crawlers import ArxivCrawler

class NetworkWorker(QThread):
    """Worker thread for network generation."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, input_str: str, data_dir: str, max_depth: int):
        super().__init__()
        self.input_str = input_str
        self.data_dir = data_dir
        self.max_depth = max_depth

    def run(self):
        try:
            # Run the async code in the thread
            network = asyncio.run(process_arxiv_input(
                self.input_str,
                self.data_dir,
                self.max_depth,
                progress_callback=self.progress.emit
            ))
            self.finished.emit(network)
        except Exception as e:
            self.error.emit(str(e))

class CitationNetworkUI(QMainWindow):
    """Main window for the citation network visualization tool."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArXiv Citation Network Visualizer")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create input widgets
        self.arxiv_input = QLineEdit()
        self.arxiv_input.setPlaceholderText("Enter ArXiv ID or URL")
        layout.addWidget(QLabel("ArXiv ID or URL:"))
        layout.addWidget(self.arxiv_input)
        
        # Depth selector
        self.depth_selector = QSpinBox()
        self.depth_selector.setRange(1, 5)
        self.depth_selector.setValue(1)
        layout.addWidget(QLabel("Citation Depth:"))
        layout.addWidget(self.depth_selector)
        
        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_display)
        
        # Buttons
        self.generate_button = QPushButton("Generate Network")
        self.generate_button.clicked.connect(self.generate_network)
        layout.addWidget(self.generate_button)
        
        # Set up data directory
        self.data_dir = Path("./arxiv_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.worker = None

    def generate_network(self):
        """Start network generation in a separate thread."""
        self.generate_button.setEnabled(False)
        self.status_display.clear()
        self.log_status("Starting network generation...")
        
        # Create and start worker thread
        self.worker = NetworkWorker(
            self.arxiv_input.text(),
            str(self.data_dir),
            self.depth_selector.value()
        )
        self.worker.finished.connect(self.on_network_generated)
        self.worker.error.connect(self.on_error)
        self.worker.progress.connect(self.log_status)
        self.worker.start()

    def on_network_generated(self, network: dict):
        """Handle the generated network."""
        self.generate_button.setEnabled(True)
        self.log_status("Network generated successfully!")
        
        # Create visualization
        self.create_network_visualization(network)
        self.log_status("Visualization saved to 'citation_network.html'")

    def on_error(self, error_msg: str):
        """Handle any errors during network generation."""
        self.generate_button.setEnabled(True)
        self.log_status(f"Error: {error_msg}")

    def log_status(self, message: str):
        """Add a message to the status display."""
        self.status_display.append(message)

    def create_network_visualization(self, network: dict):
        """Create an interactive network visualization using PyVis."""
        net = Network(
            height="750px",
            width="100%",
            bgcolor="#ffffff",
            font_color="#333333"
        )
        
        # Configure physics
        net.barnes_hut(
            gravity=-2000,
            central_gravity=0.3,
            spring_length=200,
            spring_strength=0.05,
            damping=0.09,
            overlap=0
        )
        
        # Add nodes
        for node_id, node_data in network['nodes'].items():
            title = f"Title: {node_data['title']}<br>Authors: {', '.join(node_data['authors'])}"
            net.add_node(
                node_id,
                label=f"{node_id}",
                title=title,
                color=self.get_node_color(node_data['depth'])
            )
        
        # Add edges
        for edge in network['edges']:
            net.add_edge(
                edge['source'],
                edge['target'],
                title=edge.get('citation', ''),
                arrows='to'
            )
        
        # Save visualization
        net.show("citation_network.html")

    @staticmethod
    def get_node_color(depth: int) -> str:
        """Get color for node based on depth."""
        colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
        return colors[min(depth, len(colors) - 1)]

async def process_arxiv_input(input_str: str, data_dir: str = "./data", 
                            max_depth: int = 1, verbose: bool = False,
                            progress_callback=None):
    """
    Process ArXiv paper input (URL or ID) and crawl its citation network.
    
    Args:
        input_str: ArXiv ID or URL (supports multiple formats)
        data_dir: Directory to store downloaded papers
        max_depth: Maximum depth for citation crawling
        verbose: Whether to print detailed progress
        progress_callback: Optional callback for progress updates
        
    Example inputs:
        - "1706.03762"
        - "https://arxiv.org/abs/1706.03762"
        - "https://arxiv.org/pdf/1706.03762.pdf"
    """
    # Initialize crawler with specified data directory
    arxiv = ArxivCrawler(data_dir=data_dir)
    
    # Create data directory if it doesn't exist
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    def update_progress(message):
        """Update progress using callback if available."""
        if progress_callback:
            progress_callback(message)
        if verbose:
            print(message)

    # Extract ArXiv ID from input (handles URLs)
    arxiv_id = arxiv.extract_arxiv_id(input_str)
    update_progress(f"Extracted ArXiv ID: {arxiv_id}")
    update_progress(f"Starting crawl with max depth {max_depth}")
    
    # First get the paper info to verify it exists
    paper_info = await arxiv.fetch_paper_info(arxiv_id)
    if 'error' in paper_info:
        raise ValueError(f"Could not fetch paper: {paper_info['error']}")
    
    update_progress(f"Initial paper: {paper_info['title']}")
    
    # Generate citation network
    network = await arxiv.generate_citation_network(
        seed_papers=[arxiv_id],
        max_depth=max_depth
    )
    
    # Print statistics
    node_count = len(network.get('nodes', {}))
    edge_count = len(network.get('edges', []))
    update_progress(f"Generated network with {node_count} nodes and {edge_count} edges")
    
    return network

def main():
    """Run the GUI application."""
    app = QApplication(sys.argv)
    window = CitationNetworkUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()