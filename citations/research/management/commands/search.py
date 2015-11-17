import os
import sys
import webbrowser

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from taggit.models import Tag, TaggedItem

from publications.bibtex import save_bib
from publications.models import Publication

if sys.version_info[0] < 3:
    input = raw_input

from citations.research.scholar import (
    SearchScholarQuery, ScholarQuerier, ScholarSettings, ScholarConf)

ScholarConf.MAX_PAGE_RESULTS = 1
ScholarConf.LOG_LEVEL = 3

# take a env variable, if present,
# fallback to default path, if available
# else, run without a cookie
default_cookie_path = os.path.join(
    settings.BASE_DIR, 'citations/research/cookies.txt')
if not os.path.isfile(default_cookie_path):
    default_cookie_path = None
ScholarConf.COOKIE_JAR_FILE = os.environ.get('SCHOLAR_COOKIE_PATH', default_cookie_path)
if not ScholarConf.COOKIE_JAR_FILE:
    print('Warning: running without cookie file.')

querier = ScholarQuerier()
settings = ScholarSettings()
query = SearchScholarQuery()

#settings.set_citation_format(ScholarSettings.CITFORM_BIBTEX)
# network call on import!
#querier.apply_settings(settings)

def sinput(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print()
        sys.exit(0)


class Command(BaseCommand):
    help = 'Search words and pull in citations'

    def add_arguments(self, parser):
        parser.add_argument('words', nargs='+', type=str)

        # year range
        parser.add_argument(
            '--after',
            type=int,
            dest='after'
        )
        parser.add_argument(
            '--before',
            type=int,
            dest='before'
        )
        # number of results
        parser.add_argument(
            '--num',
            type=int,
            dest='num'
        )
        # 0-based offset
        parser.add_argument(
            '--start',
            type=int,
            dest='start'
        )

    def handle(self, *args, **options):
        options['num'] = options.get('num') or ScholarConf.MAX_PAGE_RESULTS
        options['start'] = options.get('start') or 0
        print(options)

        if options.get('after') or options.get('before'):
            query.timeframe = [options.get('after'), options.get('before')]

        query.start = options.get('start', 0)
        query.num_results = options['num']
        query.words = " ".join(options['words'])
        querier.send_query(query)

        for article in querier.articles:
            #querier.get_citation_data(article)
            print()
            print()
            print(article.as_txt())
            if article['url']:
                res = sinput('Open in browser? (Y/n) ')
                if res in ['Y', 'y', '']:
                    webbrowser.open(article['url'])

            res = sinput('Cite? (Y/n) ')
            if res in ['Y', 'y', '']:
                querier.get_citation_data(article)
                pub = save_bib(article.as_citation())[0]

                if pub._created:
                    print('Created')
                else:
                    print('Already present')

                if article['url']:
                    pub.url = article['url']
                if article['excerpt']:
                    pub.excerpt = article['excerpt']

                pub.save()

                tag = True
                while tag:
                    tag = sinput('Add tag: ')
                    if tag:
                        pub.add_tag(tag)

        # Ctrl+C to quit
        print(options)
        new_words = sinput('New query? Enter words: ')
        self.handle(
            words=new_words.split(' ') if new_words else options['words'],
            after=int(sinput('After: ') or 0) or options.get('after'),
            before=int(sinput('Before: ') or 0) or options.get('before'),
            num=int(sinput('Num: ') or 0) or options.get('num'),
            start=(sinput('Start num: ') or 0)
                or int(options['start']) + int(options['num'])
        )



