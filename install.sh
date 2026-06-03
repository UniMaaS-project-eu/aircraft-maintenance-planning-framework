python -m venv .venv
source .venv/bin/activate
git clone https://github.com/UniMaaS-project-eu/aircraft-level-planning-tcpn.git TCPN;
git clone https://github.com/UniMaaS-project-eu/WP5-QUB-Aegean TACPN/TACPN_generator;
pip install -r requirements.txt
cd TCPN
git submodule update --init --recursive
cd cpn-py
pip install -e .