1. Auto install deps and start server
   ```
   uv run server.py
   ```
2. Test the server
   ```
   curl http://localhost:3001/health
   ```
3. Open `index.html` with Live Server and search

Toggle LanceDB Vector search should call the /search endpoint on server terminal.

I embedded all 5772 NeurIPS papers into LanceDB. You can replace the database with your own data by changing the `DB_PATH` variable in `server.py`.

![Demo](demo.gif)
