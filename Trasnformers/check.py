import json

# Change the file name here if needed
file_to_check = 'errors_to_fix.json'

# List to store all errors found
all_errors = []

# List to store the starting line number of each record
record_start_lines = []


def validate_record(record, index):
    """
    This function validates one record, which is one JSON object.
    It checks that the structure is fully correct.
    """
    errors = []

    if not isinstance(record, dict):
        errors.append(
            f"  -> The item is not an object. It is of type '{type(record).__name__}'."
        )
        return errors

    expected_keys = {"question", "context", "answers"}
    record_keys = set(record.keys())

    if record_keys != expected_keys:
        errors.append(
            f"  -> Main keys are incorrect. Expected: {expected_keys}, found: {record_keys}"
        )

    if 'question' in record and not isinstance(record['question'], str):
        errors.append(
            f"  -> Error in 'question': it should be a string, "
            f"but the current type is '{type(record['question']).__name__}'."
        )

    if 'context' in record and not isinstance(record['context'], str):
        errors.append(
            f"  -> Error in 'context': it should be a string, "
            f"but the current type is '{type(record['context']).__name__}'."
        )

    if 'answers' in record and not isinstance(record['answers'], dict):
        errors.append(
            f"  -> Error in 'answers': it should be an object/dictionary, "
            f"but the current type is '{type(record['answers']).__name__}'."
        )
        return errors

    answers_obj = record.get('answers', {})
    expected_answers_keys = {"text", "answer_start"}
    answers_keys = set(answers_obj.keys())

    if answers_keys != expected_answers_keys:
        errors.append(
            f"  -> Error in 'answers': internal keys are incorrect. "
            f"Expected: {expected_answers_keys}, found: {answers_keys}"
        )

    if 'text' in answers_obj and not isinstance(answers_obj['text'], list):
        errors.append(
            f"  -> Error in 'answers' -> 'text': it should be a list, "
            f"but the current type is '{type(answers_obj['text']).__name__}'."
        )

    if 'answer_start' in answers_obj and not isinstance(answers_obj['answer_start'], list):
        errors.append(
            f"  -> Error in 'answers' -> 'answer_start': it should be a list, "
            f"but the current type is '{type(answers_obj['answer_start']).__name__}'."
        )

    return errors


# Main program starts here
try:
    print(f"Checking the structure of file: {file_to_check} ...")

    # Detect the approximate starting line numbers of records
    with open(file_to_check, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        # Look for lines that start with "{" and mark the beginning of a record.
        # This assumes that the file is well formatted / pretty-printed.
        in_main_list = False

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            if stripped_line.startswith('['):
                in_main_list = True

            # If we are inside the main list and find a line starting with "{",
            # this is considered the beginning of a new record.
            if in_main_list and stripped_line.startswith('{'):
                record_start_lines.append(i + 1)

    # Reopen the file to load it as JSON and validate it
    with open(file_to_check, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("\nMain error: the file does not start with a list [].")
    else:
        # Loop through each record in the main list
        for index, record in enumerate(data):
            errors_found = validate_record(record, index)

            if errors_found:
                # Try to get the line number that matches the record index
                line_number_info = "not specified"

                if index < len(record_start_lines):
                    line_number_info = (
                        f"starts approximately at line {record_start_lines[index]}"
                    )

                # Add the error message with the record number and line number
                all_errors.append(f"- In record number [{index}] ({line_number_info}):")
                all_errors.extend(errors_found)

    # Display the final results after validation
    if not all_errors:
        print("\nEverything looks good. The data structure matches the required format.")
    else:
        print("\nErrors were found in the data structure.")

        for error_message in all_errors:
            print(error_message)

except FileNotFoundError:
    print(f"\nError: the file '{file_to_check}' was not found.")

except json.JSONDecodeError as e:
    print(
        f"\nError: the file '{file_to_check}' is not a valid JSON file. "
        f"There is an issue near line {e.lineno}, column {e.colno}."
    )

except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
