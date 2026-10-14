"""First look: sizes, preterm rate by group, and a district map of the preterm share.
Run from the repo root:  python examples/01_explore.py"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from common import participants, DATA, ROOT

df = participants()
print(f'{len(df):,} pregnancies, {df.district_id.nunique()} districts, births {df.birth_date.min().date()} to {df.birth_date.max().date()}')
print(f'preterm {df.preterm.mean():.3f}, very preterm {df.very_preterm.mean():.3f}, stillbirth {df.stillbirth.mean():.3f}')
for col in ['country', 'ses_grade', 'outdoor_work_pregnancy', 'hiv_positive', 'urban_rural']:
    print(df.groupby(col).preterm.agg(['mean', 'size']).round(3).to_string(), '\n')

rate = df.groupby('district_id').preterm.mean()
gj = json.load(open(DATA / 'districts.geojson'))
fig, ax = plt.subplots(figsize=(6, 6))
patches, vals = [], []
for f in gj['features']:
    patches.append(Polygon(f['geometry']['coordinates'][0], closed=True)); vals.append(100 * rate[f['properties']['district_id']])
pc = PatchCollection(patches, cmap='Greys', edgecolor='white', linewidth=0.3); pc.set_array(vals); ax.add_collection(pc)
ax.autoscale(); ax.set_aspect('equal'); plt.colorbar(pc, ax=ax, label='Preterm births (%)', fraction=0.04)
ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude')
out = ROOT / 'figures' / 'example_district_preterm.png'; fig.savefig(out, dpi=150, bbox_inches='tight'); print('saved', out)
