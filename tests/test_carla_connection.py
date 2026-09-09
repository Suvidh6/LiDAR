"""
tests/test_carla_connection.py
Checks connectivity to local CARLA 0.9.16 server.
"""

def test_carla_connection(host="localhost", port=2000):
    try:
        import carla
        client = carla.Client(host, port)
        client.set_timeout(3.0)
        world = client.get_world()
        map_name = world.get_map().name
        print(f"CARLA connection SUCCESSFUL! Connected to map: {map_name}")
        return True
    except Exception as e:
        print(f"CARLA server not running on {host}:{port} ({e}). (Offline mode active)")
        return False

if __name__ == "__main__":
    test_carla_connection()
