from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def parse_time(time_str):
    formats = ["%I:%M %p", "%I:%M%p", "%H:%M"]
    for fmt in formats:
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    intervals = data.get('intervals', [])

    if not intervals:
        return jsonify({'error': 'Please add at least one time interval.'}), 400

    total_seconds = 0
    breakdown = []

    for i, interval in enumerate(intervals):
        start_str = interval.get('start')
        end_str = interval.get('end')

        if not start_str or not end_str:
            return jsonify({'error': f'Missing time in row {i+1}.'}), 400

        start_dt = parse_time(start_str)
        end_dt = parse_time(end_str)

        if not start_dt or not end_dt:
            return jsonify({'error': f'Invalid format in row {i+1}. Try "1:10 pm".'}), 400

        if end_dt < start_dt:
            end_dt += timedelta(days=1)

        duration = end_dt - start_dt
        seconds = int(duration.total_seconds())
        total_seconds += seconds
        
        # Optional: Calculate individual row duration for breakdown if needed
        row_hours = seconds // 3600
        row_minutes = (seconds % 3600) // 60
        breakdown.append({
            'start': start_str, 
            'end': end_str, 
            'hours': row_hours, 
            'minutes': row_minutes
        })

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    result_parts = []
    if hours > 0:
        result_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        result_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if not result_parts:
        result_text = "0 minutes"
    else:
        result_text = " ".join(result_parts)

    return jsonify({'result': result_text, 'hours': hours, 'minutes': minutes, 'breakdown': breakdown})

if __name__ == '__main__':
    app.run(debug=True)
