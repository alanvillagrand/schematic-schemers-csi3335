import re


def add_columns_to_queries(file_path):
    # Read the input file
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex pattern to match db.session.query(People.nameFirst, People.nameLast, ...)
    query_pattern = r"db\.session\.query\((People\.nameFirst,\s*People\.nameLast)(.*?)\)"

    # Function to add debutDate and finalGameDate if not already present
    def modify_query(match):
        existing_columns = match.group(2)

        # Check if debutDate or finalGameDate are already in the query
        if "People.debutDate" not in existing_columns and "People.finalGameDate" not in existing_columns:
            # Add debutDate and finalGameDate
            updated_query = f"db.session.query({match.group(1)}, People.debutDate, People.finalGameDate{existing_columns})"
            return updated_query
        return match.group(0)  # Return the original match if no modification is needed

    # Replace all relevant query patterns
    updated_content = re.sub(query_pattern, modify_query, content)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(updated_content)

    print(f"Updated queries in {file_path}")


add_columns_to_queries('immaculateGridQueries.py')

