# lol_id_tools
An id tool for League of Legends with fuzzy string matching, nicknames, multiple locales, automatic updates, and translation.

The package relies on [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) for string matching. Nicknames are on 
[github](https://github.com/mrtolkien/lol_id_tools/blob/master/data/nicknames.json), please make a pull requests to 
add new ones!

# Installation

Get lit with `pip install lol-id-tools`

# Usage
## Initialisation
```python
import lol_id_tools

# lit will always reload existing locales, and try to add any supplied as arguments.
lit = lol_id_tools.LolIdTools('en_US', 'ko_KR')
```
## Get id from name
```python
# When the name is typed properly, matching is instant.
lit.get_id('Miss Fortune')
```
> 21

```python
# Standard nicknames are loaded from https://github.com/mrtolkien/lol_id_tools/blob/master/data/nicknames.json.
lit.get_id('MF')
```
> 21

```python
# Any loaded locale will work
lit.get_id('미스 포츈')
```
> 21

```python
# Even very inaccurate strings can match properly, but the package will raise a warning if its confidence is low.
lit.get_id('misfo')
```
> WARNING:root:	Very low confidence matching from misfo to Miss Fortune.
> 
>Type: champion, Locale: en_US, Precision ratio: 59
>
> 21
---
```python
lit.get_id('Maw of Malmortius')
```
> 3156

```python
# This matches to Kog'Maw because of our calculation method and is an unwanted result.
lit.get_id('Maw of Malmo')
```
> 96

```python
# When we know the type of object we are looking for, we can improve accuracy by providing input_type
lit.get_id('Maw of Malmo', input_type='item')
```
> 3156

## Get name from ID
On patch 10.5 no champion, item, or rune shares an ID. If they do in the future, the package will need to be
updated accordingly.

```python
lit.get_name(11)
```
> 'Master Yi'

```python
# If a locale needed for output is not loaded, it will automatically add it to the package.
lit.get_name(11, 'fr_FR')
```
> 'Maître Yi'

## Get translation
```python
# Default output is 'en_US'
lit.get_translation('미스 포츈')
```
> 'Miss Fortune'

```python
# If you haven’t loaded the input locale yet, you can supply it as a parameter
lit.get_translation('ミス・フォーチュン', 'zh_CN', input_locale='ja_JP')
```
> '赏金猎人'

```python
# If get_translation() is called on an existing locale, it can help get the "clean" object name
lit.get_translationn('Misfo')
```
> WARNING:root:	Very low confidence matching from Misfo to Miss Fortune.
> 
> Type: champion, Locale: en_US, Precision ratio: 59
>
> 'Miss Fortune'


## Handling locales
```python
# Adds Polish language information
lit.add_locale('pl_PL')
```

```python
# Forces reloading of all existing locales
lit.reload_app_data()
```

```python
# Reloads and saves data with only the specified locales
lit.reload_app_data('en_US', 'ja_JP')
```

## Tests

You can take a look at the [tests suit](https://github.com/mrtolkien/lol_id_tools/tree/master/lol_id_tools/_tests) 
for more code examples.

## Notes

Package data is saved in `~/.config/lol_id_tools` for offline usage and faster startup after first use. 
If loading all 27 LoL locales, dump size is 205kbs.