python3 -m venv .venv &&
source .venv/bin/activate &&
pip install -r requirements.txt &&
git clone https://github.com/UniMaaS-project-eu/WP5-QUB-Aegean TACPN/TACPN_generator || echo "skipping TACPN (remove TACPN/TACPN_generator directory if you want full reinstall)" &&
git clone https://github.com/SeekerRook/cpn-py  || echo "skipping cpn-py installation (remove TCPN directory if you want full reinstall)" &&
cd cpn-py &&
pip install -e .