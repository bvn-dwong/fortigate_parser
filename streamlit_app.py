import streamlit as st
import re

# Function to parse the Fortigate configuration file
def parse_config(file_content):
    config_sections = {}
    section_stack = []  # Stack to keep track of section hierarchy

    for line in file_content.split('\n'):
        if line.strip().startswith('config '):
            section_name = line.strip().split(' ', 1)[1]
            section_stack.append((section_name, [line]))
        elif line.strip() == 'end' and section_stack:
            section_name, section_lines = section_stack.pop()
            section_lines.append(line)
            full_section_name = ' > '.join([name for name, _ in section_stack] + [section_name])
            config_sections[full_section_name] = '\n'.join(section_lines)
            if section_stack:
                section_stack[-1][1].extend(section_lines)
        elif section_stack:
            section_stack[-1][1].append(line)

    return config_sections

# Function to search for sections by name and content
def search_sections(sections, query):
    pattern = re.compile(re.escape(query).replace('\\*', '.*'), re.IGNORECASE)
    return {name: content for name, content in sections.items() if pattern.match(name) or pattern.search(content)}

# Streamlit app layout
st.title("Fortigate Config Parser")

# File uploader
uploaded_file = st.file_uploader("Upload a Fortigate configuration file", type=['conf'])
if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("utf-8")
    parsed_config = parse_config(file_content)

    # Search functionality
    with st.sidebar:
        st.title("Search Sections")
        search_query = st.text_input("Enter search query (use * for wildcard)")
        search_results = search_sections(parsed_config, search_query)
        selected_section = st.selectbox("Select a section", options=list(search_results.keys()), index=0)

    # Display and download functionality
    if selected_section:
        st.write(f"Contents of section {selected_section}:")
        section_content = search_results[selected_section]
        st.text_area("Section Content", value=section_content, height=300)

        # Direct implementation of the download button
        download_filename = f"{selected_section.replace(' > ', '_')}.txt"
        st.download_button(
            label="Download This Section",
            data=section_content,
            file_name=download_filename,
            mime='text/plain'
        )
