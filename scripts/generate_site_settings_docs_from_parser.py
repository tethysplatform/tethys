# flake8: noqa

import re
import inspect
from django.utils import timezone
from tethys_cli.site_commands import add_site_parser


args = re.findall("add_argument\(.*?dest='(.*?)'.*?help='(.*?)'\)", inspect.getsource(add_site_parser), re.DOTALL)

args_dict = {arg[0]: arg[1] for arg in args}
args_dict.pop('restore_defaults')

custom_templates_settings = {k: v for k, v in args_dict.items() if k.endswith('template')}
custom_styles_settings = {k: v for k, v in args_dict.items() if k.endswith('css')}
home_page_settings = {k: v for k, v in args_dict.items()
                      if k.split('_')[0].upper() in ['HERO', 'BLURB', 'FEATURE', 'CALL']}
general_settings = {k: v for k, v in args_dict.items()
                    if k not in set(custom_styles_settings).union(custom_styles_settings).union(home_page_settings)}

output = ''

col1_len = 30
col2_len = 80

table_sep = f'{"=" * col1_len} {"=" * col2_len}'

table_header = f'{table_sep}\n{"Setting":<{col1_len}} {"Description":<{col2_len}}\n{table_sep}\n'

for category, settings in {
    'GENERAL_SETTINGS': general_settings,
    'HOME_PAGE': home_page_settings,
    'CUSTOM_STYLES': custom_styles_settings,
    'CUSTOM_TEMPLATES': custom_templates_settings,
}.items():
    output += f'\n{category}\n{"+" * len(category)}\n\n{table_header}'
    for k, v in settings.items():
        v = re.sub("[\s']+", ' ', v)
        output += f'{k.upper():<{col1_len}} {v:<{col2_len}}\n'
    output += f'{table_sep}\n'

output = output.replace('A double quoted string', 'A string')
output = output.replace('f Default is "Copyright © {timezone.now():%Y}', f'Default is "Copyright © {timezone.now():%Y}')

print(output)
