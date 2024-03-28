
def write_page_source(name: str, page_source: str):
    """
    Writes the page source to a file.

    Args:
        url (str): The URL of the page.
        page_source (str): The page source to be written.

    Returns:
        None
    """
    # Replace special characters in the URL to create a valid file name
    file_name = f"outputs/{name}.html"
    # Write the page source to the file
    with open(file_name, "w") as file:
        file.write(page_source)
