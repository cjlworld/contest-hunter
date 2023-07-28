from app import create_app
import config

# 创建 app
app = create_app(config.config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
