from app.dashboard import create_app

app = create_app()

if __name__ == '__main__':
    print(" * Flask 서버를 시작합니다...")
    print(" * 접속 주소: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
