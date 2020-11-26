mkdir -p ~/.streamlit/
echo "[general]
email = \"ak7907@nyu.edu\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml