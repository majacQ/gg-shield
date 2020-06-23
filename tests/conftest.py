_MULTIPLE_SECRETS_PATCH = """@@ -0,0 +1,2 @@
+FacebookAppKeys :
+String docker run --name geonetwork -d \
            -p 8080:8080 -e MYSQL_HOST=google.com \
            -e MYSQL_PORT=5434 -e MYSQL_USERNAME=root \
            -e MYSQL_PASSWORD=m42ploz2wd geonetwork
"""

    """diff --git a/test.txt b/test.txt
new file mode 100644
index 0000000..b80e3df
--- /dev/null
+++ b/test
"""
    + _MULTIPLE_SECRETS_PATCH
        "policies": ["Secrets detection", "File extensions", "Filenames"],
                        "index_start": 114,
                        "index_end": 123,
                        "line_end": 3,
                        "index_start": 151,
                        "index_end": 154,
                        "line_end": 3,
                        "index_start": 174,
                        "index_end": 177,
                        "line_end": 3,
                        "index_start": 209,
                        "index_end": 218,
                        "line_end": 3,
_SIMPLE_SECRET_WITH_FILENAME_PATCH_SCAN_RESULT = ScanResult.SCHEMA.load(
    {
        "policies": ["File extensions", "Filenames", "Secrets detection"],
        "policy_breaks": [
            {
                "type": ".env",
                "policy": "Filenames",
                "matches": [{"type": "filename", "match": ".env"}],
            },
            {
                "type": "GitHub Token",
                "policy": "Secrets Detection",
                "matches": [
                    {
                        "match": "368ac3edf9e850d1c0ff9d6c526496f8237ddf91",  # noqa
                        "type": "apikey",
                        "index_start": 29,
                        "index_end": 69,
                    }
                ],
            },
        ],
        "policy_break_count": 2,
    }
)
