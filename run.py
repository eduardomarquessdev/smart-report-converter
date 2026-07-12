from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("  Conversor TXT -> XLSX")
    print("=" * 50)
    print("  Acesse: http://localhost:5000")
    print("  Pressione Ctrl+C para parar.")
    print("=" * 50)
    app.run(debug=False, port=5000)
