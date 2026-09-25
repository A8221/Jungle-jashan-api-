from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

CREATE_URL = (
    BASE_URL +
    "/services/aigc/image2video/video-synthesis"
)

TASK_URL = BASE_URL + "/tasks/"


@app.get("/")
def home():
    return jsonify({
        "success": True,
        "service": "Jungle Jashan Wan2.2 API",
        "status": "online"
    })


@app.post("/generate")
def generate():

    data = request.get_json(silent=True) or {}

    image_url = data.get("image_url", "")
    audio_url = data.get("audio_url", "")

    if not DASHSCOPE_API_KEY:
        return jsonify({
            "success": False,
            "message": "DASHSCOPE_API_KEY is missing"
        }), 500

    if not image_url:
        return jsonify({
            "success": False,
            "message": "image_url is required"
        }), 400

    if not audio_url:
        return jsonify({
            "success": False,
            "message": "audio_url is required"
        }), 400

    payload = {
        "model": "wan2.2-s2v",
        "input": {
            "image_url": image_url,
            "audio_url": audio_url
        },
        "parameters": {
            "resolution": "480P"
        }
    }

    headers = {
        "Authorization": "Bearer " + DASHSCOPE_API_KEY,
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }

    try:

        response = requests.post(
            CREATE_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        result = response.json()

        if response.status_code not in range(200, 300):

            return jsonify({
                "success": False,
                "message": result
            }), response.status_code

        output = result.get("output", {})

        task_id = output.get("task_id", "")

        if not task_id:

            return jsonify({
                "success": False,
                "message": "Task ID not received",
                "response": result
            }), 500

        return jsonify({
            "success": True,
            "task_id": task_id,
            "status": output.get(
                "task_status",
                "PENDING"
            )
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.get("/status/<task_id>")
def status(task_id):

    if not DASHSCOPE_API_KEY:
        return jsonify({
            "success": False,
            "message": "DASHSCOPE_API_KEY is missing"
        }), 500

    headers = {
        "Authorization": "Bearer " + DASHSCOPE_API_KEY
    }

    try:

        response = requests.get(
            TASK_URL + task_id,
            headers=headers,
            timeout=60
        )

        result = response.json()

        if response.status_code not in range(200, 300):

            return jsonify({
                "success": False,
                "message": result
            }), response.status_code

        output = result.get("output", {})

        status_value = output.get(
            "task_status",
            "UNKNOWN"
        )

        video_url = ""

        results = output.get("results", {})

        if isinstance(results, dict):
            video_url = results.get(
                "video_url",
                ""
            )

        if not video_url:
            video_url = output.get(
                "video_url",
                ""
            )

        return jsonify({
            "success": True,
            "task_id": task_id,
            "status": status_value,
            "video_url": video_url,
            "message": output.get(
                "message",
                ""
            )
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "8080"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
