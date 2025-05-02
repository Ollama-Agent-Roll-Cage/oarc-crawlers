"""
ArXiv Crawler Examples with Network Visualization

This script demonstrates:
1. Crawling papers and their citation networks
2. Handling different ArXiv URL formats
3. Saving data in Parquet format
4. Visualizing citation networks using PyVis
5. Interactive GUI using PyQt6 with modern dark theme
"""

import asyncio
from pathlib import Path
import sys
from typing import List, Optional, Union
import json

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QLineEdit, QSpinBox, QLabel, QTextEdit, QFrame, QHBoxLayout)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from pyvis.network import Network

from oarc_crawlers import ArxivCrawler
from PyQt6.QtWebEngineWidgets import QWebEngineView  # Add this import
from PyQt6.QtCore import QUrl

# Modern dark theme styles
STYLE_SHEET = """
QMainWindow {
    background-color: #1a1b26;
}
QWidget {
    background-color: #1a1b26;
    color: #a9b1d6;
    font-family: 'Segoe UI', sans-serif;
}
QLineEdit, QSpinBox {
    background-color: #24283b;
    border: 2px solid #414868;
    border-radius: 8px;
    padding: 5px;
    color: #a9b1d6;
    font-size: 14px;
}
QPushButton {
    background-color: #7aa2f7;
    color: #1a1b26;
    border: none;
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #89b4fa;
}
QPushButton:disabled {
    background-color: #414868;
    color: #565f89;
}
QTextEdit {
    background-color: #24283b;
    border: 2px solid #414868;
    border-radius: 8px;
    padding: 5px;
    color: #a9b1d6;
    font-size: 13px;
}
QLabel {
    color: #7aa2f7;
    font-size: 14px;
    font-weight: bold;
}
"""

class CardFrame(QFrame):
    """Custom card-style frame with modern styling."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            CardFrame {
                background-color: #24283b;
                border: 2px solid #414868;
                border-radius: 12px;
                padding: 10px;
                margin: 5px;
            }
        """)

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
        self.setGeometry(100, 100, 1200, 800)  # Made window larger
        self.setStyleSheet(STYLE_SHEET)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create horizontal layout for left panel and visualization
        horizontal_layout = QHBoxLayout(main_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Input card
        input_card = CardFrame()
        input_layout = QVBoxLayout(input_card)
        
        # ArXiv input
        self.arxiv_input = QLineEdit()
        self.arxiv_input.setPlaceholderText("Enter ArXiv ID or URL (e.g., 1706.03762)")
        input_layout.addWidget(QLabel("ArXiv ID or URL:"))
        input_layout.addWidget(self.arxiv_input)
        
        # Save location input
        self.save_location = QLineEdit()
        self.save_location.setPlaceholderText("Enter save location (optional)")
        input_layout.addWidget(QLabel("Save Location:"))
        input_layout.addWidget(self.save_location)
        
        # Depth selector
        depth_widget = QWidget()
        depth_layout = QHBoxLayout(depth_widget)
        depth_layout.setContentsMargins(0, 0, 0, 0)
        
        self.depth_selector = QSpinBox()
        self.depth_selector.setRange(1, 5)
        self.depth_selector.setValue(1)
        depth_layout.addWidget(QLabel("Citation Depth:"))
        depth_layout.addWidget(self.depth_selector)
        depth_layout.addStretch()
        input_layout.addWidget(depth_widget)
        
        left_layout.addWidget(input_card)
        
        # Status card
        status_card = CardFrame()
        status_layout = QVBoxLayout(status_card)
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMinimumHeight(150)
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_display)
        
        left_layout.addWidget(status_card)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Generate button
        self.generate_button = QPushButton("Generate Network")
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.clicked.connect(self.generate_network)
        self.generate_button.setMinimumHeight(50)
        button_layout.addWidget(self.generate_button)
        
        # Save button
        self.save_button = QPushButton("Save Network")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.clicked.connect(self.save_network)
        self.save_button.setMinimumHeight(50)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        
        # Add left panel to main layout
        horizontal_layout.addWidget(left_panel, stretch=40)
        
        # Add web view for visualization
        self.web_view = QWebEngineView()
        self.web_view.setMinimumWidth(600)
        horizontal_layout.addWidget(self.web_view, stretch=60)
        
        # Set up data directory
        self.data_dir = Path("./arxiv_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.worker = None
        self.current_network = None
        self.current_visualization = None

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

    def on_error(self, error_msg: str):
        """Handle any errors during network generation."""
        self.generate_button.setEnabled(True)
        self.log_status(f"Error: {error_msg}")

    def log_status(self, message: str):
        """Add a message to the status display."""
        self.status_display.append(message)

    def save_network(self):
        """Save the current network visualization."""
        if not self.current_visualization:
            self.log_status("No network to save!")
            return
            
        try:
            save_path = self.save_location.text() or "citation_network.html"
            if not save_path.endswith('.html'):
                save_path += '.html'
                
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.current_visualization)
                
            self.log_status(f"✨ Network visualization saved to: {save_path}")
        except Exception as e:
            self.log_status(f"Error saving visualization: {str(e)}")

    def create_network_visualization(self, network: dict):
        """Create an interactive network visualization using PyVis."""
        # Create network with dark theme
        net = Network(
            height="100%",
            width="100%",
            bgcolor="#1a1b26",
            font_color="#a9b1d6",
            notebook=False,
            cdn_resources="in_line"  # Add this line to include dependencies
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
        
        # Track nodes
        valid_nodes = set()
        external_nodes = set()
        
        # First add all internal nodes
        for node_id, node_data in network['nodes'].items():
            try:
                title = f"""
                <div style='background-color: #24283b; padding: 10px; border-radius: 8px; border: 2px solid #414868;'>
                    <strong style='color: #7aa2f7;'>Title:</strong> 
                    <span style='color: #a9b1d6;'>{node_data['title']}</span><br>
                    <strong style='color: #7aa2f7;'>Authors:</strong> 
                    <span style='color: #a9b1d6;'>{', '.join(node_data['authors'])}</span>
                </div>
                """
                net.add_node(
                    node_id,
                    label=f"{node_id}",
                    title=title,
                    color=self.get_node_color(node_data['depth']),
                    size=40 if node_data['depth'] == 0 else 25,  # Made nodes bigger
                    borderWidth=3,
                    borderWidthSelected=4,
                    font={'size': 14, 'color': '#a9b1d6'},
                    shape='dot'
                )
                valid_nodes.add(node_id)
            except Exception as e:
                self.log_status(f"Warning: Could not add node {node_id}: {str(e)}")

        # Count citations to each external paper
        external_citation_counts = {}
        for edge in network['edges']:
            if edge['target'] not in valid_nodes:
                external_citation_counts[edge['target']] = external_citation_counts.get(edge['target'], 0) + 1

        # Add external nodes (only if they have citations)
        for target, citation_count in external_citation_counts.items():
            try:
                net.add_node(
                    target,
                    label=target,
                    title=f"External Citation: {target}\nCited {citation_count} times",
                    color='#414868',
                    size=15 + min(citation_count * 2, 20),  # Size based on citations
                    shape='diamond',
                    borderWidth=1,
                    font={'size': 12, 'color': '#565f89'}
                )
                external_nodes.add(target)
                self.log_status(f"Added external citation node: {target} (cited {citation_count} times)")
            except Exception as e:
                self.log_status(f"Warning: Could not add external node {target}: {str(e)}")

        # Add edges
        for edge in network['edges']:
            try:
                source, target = edge['source'], edge['target']
                if source in valid_nodes and (target in valid_nodes or target in external_nodes):
                    net.add_edge(
                        source,
                        target,
                        title=edge.get('citation', ''),
                        color={'color': '#7aa2f7' if target in valid_nodes else '#414868', 
                              'highlight': '#89b4fa'},
                        arrows={'to': {'enabled': True, 'scaleFactor': 0.5}},
                        width=2 if target in valid_nodes else 1
                    )
            except Exception as e:
                self.log_status(f"Warning: Could not add edge {source} → {target}: {str(e)}")

        # Add custom CSS and options
        net.set_options("""
        var options = {
            "nodes": {
                "shadow": true,
                "scaling": {"min": 20, "max": 60},
                "widthConstraint": {"minimum": 100}
            },
            "edges": {
                "smooth": {"type": "cubicBezier", "roundness": 0.5},
                "shadow": true,
                "selectionWidth": 4
            },
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -2000,
                    "springLength": 200,
                    "springConstant": 0.05,
                    "damping": 0.09,
                    "avoidOverlap": 0.5
                },
                "minVelocity": 0.75
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "multiselect": true,
                "dragNodes": true,
                "zoomView": true
            }
        }
        """)
        
        try:
            # Generate HTML with custom template that includes vis.js
            html_template = """
            <html>
            <head>
                <meta charset="utf-8">
                <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
                <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css">
            </head>
            <body>
                {network_html}
            </body>
            </html>
            """
            
            self.current_visualization = html_template.format(
                network_html=net.generate_html().replace('<html>', '').replace('</html>', '')
            )
            
            # Create a temporary file for the visualization
            temp_path = Path("temp_visualization.html")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self.current_visualization)
                
            # Load in web view
            self.web_view.setUrl(QUrl.fromLocalFile(str(temp_path.absolute())))
            
            # Enable save button
            self.save_button.setEnabled(True)
            
            self.log_status("✨ Network visualization generated successfully")
        except Exception as e:
            self.log_status(f"Error creating visualization: {str(e)}")
            raise

    @staticmethod
    def get_node_color(depth: int) -> str:
        """Get color for node based on depth with neon theme."""
        colors = ['#ff7a93', '#7aa2f7', '#9ece6a', '#e0af68', '#bb9af7']
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