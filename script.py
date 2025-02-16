from flask import Flask, request, jsonify, render_template,send_file
import pandas as pd
import ollama
import csv
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def sort_csv():
    if request.method == 'POST':
        if 'file' not in request.files or 'prompt' not in request.form:
            return jsonify({"error": "Missing file or prompt"}), 400

        file = request.files['file']
        prompt = request.form['prompt']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.endswith('.csv'):
            return jsonify({"error": "File must be a CSV"}), 400

        # Read the CSV file
        df = pd.read_csv(file)
        global sorted_df
        sorted_df = None
        # Generate sorting instructions using Ollama with DeepSeek model
        response = ollama.chat(
            model="llama3:latest",
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides Python code to sort CSV files."},
                {"role": "user", "content": f"Generate Python code to sort this DataFrame: {df.columns.tolist()}."
                f"Sort by: {prompt} and assume the file name is data.csv."
                f"Provide it to me in one singular block of code."
                f"Ensure that the block of code is demaracted by exactly 3 asterisks and a line break before and after the code block."
                f"Yet again, ensure the previously mentioned asterisks are exactly 3 in number and that there are no additional asterisks anywhere in your response."
                f"Remove the python phrase that sometimes occurs in the code that you produce."
                f"Name the sorted dataframe sorted_df."
                f"Save the sorted DataFrame to a csv file named sorted_data.csv."
                f"Add a print statement to show the first 5 rows of the sorted DataFrame using the head function"}


            ]
        )

        # Extract the Python code from the response
        code = response['message']['content'].split('``````')[0].strip()
        print(code.split("***")[1])
        code = code.split("***")[1]
        # Execute the sorting code
        try:
            exec(code,globals())
            print("run successfully?")
        except Exception as e:
            return jsonify({"error": f"Error executing sorting code: {str(e)}"}), 500

        buffer = io.BytesIO()
        sorted_df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='sorted_data.csv',
            mimetype='text/csv'
        )
    
    return render_template('provide.html')


if __name__ == '__main__':
    app.run(debug=True)