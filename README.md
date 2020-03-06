# lol_id_tools
An id getter for League of Legends with fuzzy matching, multiple locals handling, and automatic updates.

# Installation

`pip install lol-id-tools`

# Usage
```python
import lol_id_tools

lit = lol_id_tools.LolIdTools('en_US', 'ko_KR')

lit.get_id('Miss Fortune')
">>> 21"
lit.get_id('MF')
">>> 21"
lit.get_id('misfone')
">>> 21"
lit.get_id('misfon')
">>> WARNING:root:Very low confidence matching from misfon to Sion. Type: champion, Locale: fr_FR"
">>> 14"

lit.get_id('미스 포츈')
">>> 21"

lit.get_id('Kai’Sa')
">>> 145"

lit.get_id('Grasp')
">>> 8437"

lit.get_name(11, 'fr_FR')
">>> 'Maître Yi'"

lit.get_translation('Nunu')
">>> '누와 윌럼프'"

lit.get_id('12121121')
">>> WARNING:root:Very low confidence matching from 12121121 to Hextech Protobelt-01. Type: item, Locale: en_US, Ratio 11"
">>> 3152"
```