python3 -m venv .venv &&
source .venv/bin/activate &&
pip install -r requirements.txt &&
git clone https://github.com/UniMaaS-project-eu/WP5-QUB-Aegean TACPN/TACPN_generator || echo "skipping TACPN (remove TACPN/TACPN_generator directory if you want full reinstall)" &&
git clone https://github.com/UniMaaS-project-eu/aircraft-level-planning-tcpn.git TCPN || echo "skipping TCPN (remove TCPN directory if you want full reinstall)" &&
cd TCPN &&
git submodule update --init --recursive &&
cd cpn-py &&
pip install -e .