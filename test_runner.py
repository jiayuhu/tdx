import sys
print("TEST SCRIPT STARTING", flush=True)
sys.stdout.flush()
try:
    from xg import main
    print("Imported main", flush=True)
    main()
except Exception as e:
    print(f"Exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
print("SCRIPT DONE", flush=True)
