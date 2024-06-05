from rest_framework.renderers import JSONRenderer
import json
import uuid

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

class SingleEscapeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict) and 'data' in data:
            for item in data['data']:
                if 'message' in item and isinstance(item['message'], str):
                    item['message'] = self._convert_to_unicode_escape(item['message'])
        # Ensure the result is a bytestring
        rendered_data = json.dumps(data, cls=CustomJSONEncoder).replace("\\\\", "\\")
        return rendered_data.encode('utf-8')

    def _convert_to_unicode_escape(self, text):
        # Convert each character in the text to its Unicode escape sequence
        escaped_text = ''
        for char in text:
            if ord(char) > 0xFFFF:
                # Convert character to surrogate pairs
                char_code = ord(char)
                high_surrogate = 0xD800 + (char_code - 0x10000) // 0x400
                low_surrogate = 0xDC00 + (char_code - 0x10000) % 0x400
                escaped_text += f'\\u{high_surrogate:04x}\\u{low_surrogate:04x}'
            else:
                escaped_text += f'\\u{ord(char):04x}'
        return escaped_text
