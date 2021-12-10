# Google Drive v3 Files API requests
import requests
import json

# Base URIs for Drive v3 API requests
GD_UPLOAD_BASE_URI = "https://www.googleapis.com/upload/drive/v3/files/"
GD_METADATA_BASE_URI = "https://www.googleapis.com/drive/v3/files/"


class GoogleDriveAPI:
    token = None  # the access token to use in requests

    # Constructor
    def __init__(self, token):
        super().__init__()
        self.token = token

    # Make an API endpoint request (https://requests.readthedocs.io/en/latest/api/)
    #   Input: method = request method (GET, POST, PATCH, etc.) as a string
    #          url = request url as a string
    #          url_params = dictionary of url parameters
    #          headers = dictionary of additional headers to include in the request
    #          body = request body as a string
    #   Return: a tuple of status code and response (or error) message
    #           when returned status code is 9999, the error message is
    #           an exception message
    #
    def make_request(self, method, url, url_params=dict(),
                     headers=dict(), body=None):
        # add Authorization header
        headers["Authorization"] = "Bearer " + self.token  # bearer authentication

        # make the request
        try:
            r = requests.request(method, url, headers=headers, params=url_params, data=body)
        except Exception as e:
            return 9999, str(e)

        # get the body of the response as text
        # NOTE: if the text is in json format, it can be converted to
        #       a dictionary using json.loads()
        body = r.text

        # return value contains the error message or the body
        if r.status_code > 299:
            res_dict = json.loads(body)
            ret_val = res_dict["error"]["message"]
        else:
            ret_val = body

        return r.status_code, ret_val

    # TODO: List contents of a given directory (Files:list endpoint)
    #   Input: dir_id = id of directory to list
    #                   None means user's Google Drive root directory
    #   Return: None on error, otherwise
    #           an array of dictionary objects
    #           representing the files[] list (see Drive API documentation)
    #   (ignore nextPageToken in this assignment)
    #
    def gd_list(self, dir_id=None):
        # Set up the variables to be put in the request
        if dir_id is not None:
            filter_string = "'" + str(dir_id) + "' in parents"
            params_dict = {
                "q": filter_string
            }
        elif dir_id is None:
            params_dict = None

        additional_headers = {
            "Accept": "application/json"
        }

        response_tuple = self.make_request("GET", GD_METADATA_BASE_URI, params_dict, additional_headers, None)

        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299
            #   Returns the files list
            request_response = response_tuple[1]
            request_response_dict = json.loads(request_response)
            return request_response_dict["files"]

    # TODO: Retrieve metadata about an object (Files:get endpoint)
    #   Input: res_id = id of an object (file/directory)
    #   Return: None on error, otherwise
    #           a dictionary containing the id, name and parents list
    #
    def gd_get_metadata(self, res_id):
        # Set up the variables to be put in the request
        file_uri = GD_METADATA_BASE_URI + res_id

        param_dict = {
            "fields": 'kind, id, name, parents, mimeType'
        }
        additional_headers = {
            "Accept": "application/json"
        }

        response_tuple = self.make_request("GET", file_uri, param_dict, additional_headers, None)
        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299
            #   Return a dict of the ID, name, and parents list
            request_response = response_tuple[1]
            request_response_dict = json.loads(request_response)
            return_dict = {
                "id": request_response_dict["id"],
                "name": request_response_dict["name"],
                "parents": request_response_dict["parents"]
            }
            return return_dict

    # TODO: Create a directory in a given directory (Files:create metadata uri endpoint)
    #   Input: name = name of directory to create
    #          parent_id = id of directory under which the new
    #                      directory is to be created
    #                      None means user's Google Drive root directory
    #   Return: None on error, otherwise
    #           a dictionary containing the id and name of the created directory
    #
    def gd_create_directory(self, name, parent_id=None):
        # Set up the variables to be put in the request
        additional_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accepted": "application/json"
        }

        dir_file_resource = {
            "kind": "drive#file",
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]
        }
        dfr_string = json.dumps(dir_file_resource)

        response_tuple = self.make_request("POST", GD_METADATA_BASE_URI, None, additional_headers, dfr_string)

        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299
            #   Return a dict of the ID and the name of the created file

            request_response = response_tuple[1]
            request_response_dict = json.loads(request_response)
            return_dict = {
                "id": request_response_dict["id"],
                "name": request_response_dict["name"]
            }
            return return_dict

    # TODO: Create a new file with text data in a given directory (Files:create upload uri endpoint)
    #   Input: name = name of the text file to create
    #          parent_id = id of directory under which the new
    #                      file is to be created
    #          contents = content to put in the file
    #   Return: None on error, otherwise
    #           a dictionary containing the id and name of the created file
    #
    def gd_create_text_file(self, name, parent_id, contents):
        params_dict = {
            "uploadType": "multipart"
        }
        # The headers of each content type get written in the body
        additional_headers = {
            "Content-Type": "multipart/related; boundary=separation",
            "Accepted": "*/*"
        }

        file_metadata = {
            "kind": "drive#file",
            "name": name,
            "mimeType": "application/vnd.google-apps.file",
            "parents": [parent_id]
        }
        fm_string = json.dumps(file_metadata)

        # String concatenation of the request body
        request_body = "--separation\nContent-Type: application/json\n\n" \
                       + fm_string \
                       + "\n--separation\nContent-Type: text/plain\n\n" \
                       + contents \
                       + "\n--separation--"

        response_tuple = self.make_request("POST", GD_UPLOAD_BASE_URI, params_dict, additional_headers, request_body)

        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299
            #   Return a dict of the ID and the name of the created file

            request_response = response_tuple[1]
            request_response_dict = json.loads(request_response)
            return_dict = {
                "id": request_response_dict["id"],
                "name": request_response_dict["name"]
            }
            return return_dict

    # TODO: Update text data in an existing file (Files:update upload uri endpoint)
    #   Input: file_id = id of file to update
    #          contents = new content to replace in the file
    #   Return: None on error, otherwise
    #           a dictionary containing the id and name of the updated file
    #
    def gd_update_text_file(self, file_id, contents):
        # Set up the variables to be put in the request
        request_uri = GD_UPLOAD_BASE_URI + str(file_id)

        params_dict = {
            "uploadType": "media"
        }
        additional_headers = {
            "Content-Type": "text/plain",
            "Accept": "application/json"
        }

        response_tuple = self.make_request("PATCH", request_uri, params_dict, additional_headers, contents)
        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299
            #   Return a dict of the ID and the name of the updated file
            request_response = response_tuple[1]
            request_response_dict = json.loads(request_response)
            return_dict = {
                "id": request_response_dict["id"],
                "name": request_response_dict["name"]
            }
            return return_dict

    # TODO: Export/download text contents of a file (Files:export endpoint)
    #   Input: file_id = id of file to download
    #   Return: None on error, otherwise
    #           a string containing the downloaded content
    #
    #
    def gd_export_text_file(self, file_id):
        # Set up the variables to be put in the request
        request_uri = GD_METADATA_BASE_URI + file_id + "/export"
        params_dict = {
            "mimeType": "text/plain"
        }
        additional_headers = {
            "Accept": "text/plain"
        }

        # Google returns the file as bytes
        response_tuple = self.make_request("GET", request_uri, params_dict, additional_headers, None)

        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299
            #   Return a string of the downloaded content
            return response_tuple[1]

    # TODO: Delete a file/directory (Files:delete endpoint)
    #   Input: res_id = id of file or directory to delete
    #   Return: None on error, otherwise
    #           an empty string
    #
    def gd_delete(self, res_id):
        # Set up the variables to be put in the request
        file_url = GD_METADATA_BASE_URI + res_id
        param_dict = {
            "fileId": res_id
        }
        additional_headers = {
            "Accept": "application/json"
        }

        response_tuple = self.make_request("DELETE", file_url, param_dict, additional_headers, None)

        if response_tuple[0] > 299:
            print(response_tuple[1])
            return None
        else:
            # If the returned error code is less than 299 return an empty string
            return response_tuple[1]
