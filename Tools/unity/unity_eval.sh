#!/usr/bin/env bash
# unity_eval.sh - run a C# expression in the open Unity Editor of this project and print its result.
#   Tools/unity/unity_eval.sh '<C# expression returning a value>'      (run from the project root)
# Why: `unity command eval` runs on the main thread with a 5 s limit ("Main thread operation timed out"), so anything
# longer (prefab builds, scene builds, renders) must be submitted with --detach and polled with `unity job status`.
# Notes learned on Farm Processing:
#  - After copying files into Assets/ from outside, run AssetDatabase.Refresh in its OWN call first, e.g.
#    '((System.Func<string>)(() => { UnityEditor.AssetDatabase.Refresh(UnityEditor.ImportAssetOptions.ForceUpdate); return "ok"; }))()'
#    (Refresh returns void; a build in the same call does not see the new files yet).
#  - After editing Editor C#: `unity command recompile` then poll `unity command recompile_status` until "completed".
#  - Results/errors of a failed job: `unity job status <id> --format json` -> data.result.error.
set -u
expr="$1"
j=$(unity command eval --caller plugin --skill unity-cli --project-path . --no-banner --detach "return $expr;" 2>&1 | grep -o '[0-9a-f]\{32\}' | head -1)
[ -z "$j" ] && { echo "submit failed"; exit 1; }
for i in $(seq 1 400); do
  s=$(unity job status "$j" --project-path . --no-banner --format json 2>&1)
  echo "$s" | grep -q '"state": "\(completed\|failed\|cancelled\)"' && break
  sleep 3
done
echo "$s" | python -c "import sys,json; d=json.load(sys.stdin)['data']; r=d.get('result') or {}; print(d['state']); print(r.get('result') or r.get('error') or d.get('error') or r)"
