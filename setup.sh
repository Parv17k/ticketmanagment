mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"ak7907@nyu.edu\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\