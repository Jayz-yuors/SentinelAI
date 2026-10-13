from pathlib import Path
import json, re

def generate_cyclonedx(repository: Path) -> dict:
    components=[]
    patterns={"requirements.txt": "pypi", "package.json":"npm", "pom.xml":"maven"}
    for filename, ecosystem in patterns.items():
        p=repository/filename
        if not p.exists(): continue
        text=p.read_text(encoding="utf-8",errors="replace")
        if filename=="requirements.txt":
            for line in text.splitlines():
                line=line.strip()
                if not line or line.startswith("#"): continue
                m=re.match(r"([A-Za-z0-9_.-]+)\s*(?:==|>=|<=|~=|>|<)\s*([^\s;]+)", line)
                if m:
                    components.append({"type":"library","bom-ref":f"pkg:pypi/{m.group(1).lower()}@{m.group(2)}","name":m.group(1),"version":m.group(2),"purl":f"pkg:pypi/{m.group(1).lower()}@{m.group(2)}"})
        elif filename=="package.json":
            data=json.loads(text)
            for section in ("dependencies","devDependencies"):
                for name, version in data.get(section,{}).items():
                    components.append({"type":"library","name":name,"version":version,"purl":f"pkg:npm/{name}@{version}"})
    return {"bomFormat":"CycloneDX","specVersion":"1.5","version":1,"components":components}
