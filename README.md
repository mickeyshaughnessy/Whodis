# Whodis

Entity Resolution API

## Overview

Whodis provides an interface into an entity resolution system. It allows users to query and identify entities based on provided information.

## API

Entity resolution queries can be executed through the `resolve` endpoint.

### Endpoint

POST `/resolve`

### Request Body

- `api_key` (required): Your API key for authentication
- `body` (required): JSON event-like query object representing the entity to resolve
- `resolution` (optional): Desired resolution level (0-1000, default is 0, 1000 is highest)
- `privacy` (optional): Desired amount of privacy in the query response (-1000 to 1000)

### Example Request

```json
{
  "api_key": "your_api_key_here",
  "body": {
    "name": "John Doe",
    "email": "johndoe@example.com"
  },
  "resolution": 500,
  "privacy": 100
}
```

## Privacy

Whodis allows privacy to be included as noise in query responses in two ways:

1. **Query-level privacy**: Add or remove privacy from a single query using the `privacy` parameter in the request body.

2. **Entity-specific privacy**: Inject privacy into specific entities. Future query responses containing these entities will have additional privacy.

## Support

Whodis is a free, public infrastructure project supported by donations from people like you. If you find this service valuable, please consider contributing to its development and maintenance.

## License

Whodis is licensed under the Apache License, Version 2.0. You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Contact

For questions, support, or feedback, please contact Mickey Shaughnessy on Twitter: [@mickeyshaughnes](https://twitter.com/mickeyshaughnes)