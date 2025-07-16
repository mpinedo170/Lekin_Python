def open_file(filepath):
    """
    Opens a file and returns its content.
    
    Args:
        filepath (str): Path to the file to be opened.
        
    Returns:
        str: Content of the file.
    """
    # with open(filepath, 'r') as file:
    #     content = file.read()
    # return content

    with open(filepath,'r') as f:
        content = f.read()
    return content    


opened_content = open_file("Data/Single Machine/Jobs.job")
print("File opened successfully:", opened_content)
