from flask import Flask, request, jsonify
import json
import uuid
import re
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'calendar_events.json'

DATE_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def load_events():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_events(events):
    with open(DATA_FILE, 'w') as f:
        json.dump(events, f, indent=2)


def validate_date(date_str):
    if not DATE_REGEX.match(date_str):
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


@app.route('/api/v1/calendar/items', methods=['POST'])
def create_event():
    data = request.get_data(as_text=True)

    parts = data.split('|', 2)
    if len(parts) != 3:
        return jsonify({'error': 'Invalid data format'}), 400

    date_str, title, text = parts
    date_str = date_str.strip()
    title = title.strip()
    text = text.strip()

    if not validate_date(date_str):
        return jsonify({'error': 'Invalid date format'}), 400

    if len(title) > 30:
        return jsonify({'error': 'Title too long (max 30)'}), 400

    if len(text) > 200:
        return jsonify({'error': 'Text too long (max 200)'}), 400

    events = load_events()

    if any(event['date'] == date_str for event in events):
        return jsonify({'error': 'Event already exists for this date'}), 409

    new_event = {
        'id': str(uuid.uuid4()),
        'date': date_str,
        'title': title,
        'text': text
    }

    events.append(new_event)
    save_events(events)

    return jsonify({'id': new_event['id']}), 201


@app.route('/api/v1/calendar/items', methods=['GET'])
def list_events():
    events = load_events()
    return jsonify([f"{e['date']}|{e['title']}|{e['text']}" for e in events])


@app.route('/api/v1/calendar/items/<event_id>', methods=['GET'])
def read_event(event_id):
    events = load_events()
    event = next((e for e in events if e['id'] == event_id), None)

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    return jsonify(f"{event['date']}|{event['title']}|{event['text']}")


@app.route('/api/v1/calendar/items/<event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_data(as_text=True)
    parts = data.split('|', 2)

    if len(parts) != 3:
        return jsonify({'error': 'Invalid data format'}), 400

    date_str, title, text = parts
    date_str = date_str.strip()
    title = title.strip()
    text = text.strip()

    if not validate_date(date_str):
        return jsonify({'error': 'Invalid date format'}), 400

    if len(title) > 30:
        return jsonify({'error': 'Title too long (max 30)'}), 400

    if len(text) > 200:
        return jsonify({'error': 'Text too long (max 200)'}), 400

    events = load_events()
    event = next((e for e in events if e['id'] == event_id), None)

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if any(e['date'] == date_str and e['id'] != event_id for e in events):
        return jsonify({'error': 'Event already exists for this date'}), 409

    event.update({
        'date': date_str,
        'title': title,
        'text': text
    })

    save_events(events)
    return jsonify({'status': 'success'})


@app.route('/api/v1/calendar/items/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    events = load_events()
    initial_length = len(events)
    events = [e for e in events if e['id'] != event_id]

    if len(events) == initial_length:
        return jsonify({'error': 'Event not found'}), 404

    save_events(events)
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)