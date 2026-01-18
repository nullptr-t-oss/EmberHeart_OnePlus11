import os
import sys

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def main():

    status = os.environ.get('BUILD_STATUS', 'failure') # success or failure
    release_type = os.environ.get('RELEASE_TYPE', 'release') # release or prerelease
    tag_text = os.environ.get('TAG_TEXT', 'v0.0.0')
    commit_hash = os.environ.get('COMMIT_HASH', '0000000')

    status_file = 'templates/pass.svg' if status == 'success' else 'templates/fail.svg'
    tag_file = 'templates/tag_release.svg' if release_type == 'release' else 'templates/tag_prerelease.svg'
    
    raw_status = read_file(status_file)

    final_status = raw_status 

    # Process Tag Badge
    raw_tag = read_file(tag_file)
    final_tag = raw_tag.replace('TAG_NAME', tag_text)
    
    # Process Commit Badge
    raw_commit = read_file('templates/commit.svg')
    final_commit = raw_commit.replace('COMMIT_HASH', commit_hash[:7]) # Shorten to 7 chars

    # Load Wrapper
    wrapper = read_file('templates/dashboard_template.svg')

    # Inject into Wrapper
    wrapper = wrapper.replace('{{STATUS}}', final_status)
    wrapper = wrapper.replace('{{TAG}}', final_tag)
    wrapper = wrapper.replace('{{COMMIT}}', final_commit)

    # Output
    with open('ci.svg', 'w') as f:
        f.write(wrapper)
    
    print("Dashboard SVG generated successfully.")

if __name__ == "__main__":
    main()