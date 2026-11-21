import unittest
from render_readme_cards import stats, validate, Calendar

class Tests(unittest.TestCase):
    def test_month_and_streak_boundary(self):
        days=[{'date':d,'count':n} for d,n in [('2026-01-30',2),('2026-01-31',3),('2026-02-01',1),('2026-02-02',0)]]
        months,streak,active,busiest=stats(days)
        self.assertEqual(dict(months),{'2026-01':5,'2026-02':1})
        self.assertEqual((streak,active,busiest['count']),(3,3,3))

    def test_missing_and_negative_data_rejected(self):
        for days in [[],[{'date':'2026-01-01','count':-1}],[{'date':'2026-01-01','count':1},{'date':'2026-01-03','count':1}]]:
            with self.assertRaises(ValueError): validate(days)

    def test_zero_activity(self):
        _,streak,active,busiest=stats([{'date':'2026-01-01','count':0}])
        self.assertEqual((streak,active,busiest['count']),(0,0,0))

    def test_changed_markup_fails_closed(self):
        parser=Calendar(); parser.feed('<html>Unavailable</html>')
        with self.assertRaises(ValueError): parser.days()

    def test_tooltip_counts(self):
        parser=Calendar()
        parser.feed('<tool-tip for="a">1,234 contributions on January 1st.</tool-tip><tool-tip for="b">No contributions on January 2nd.</tool-tip>')
        self.assertEqual(parser.counts,{'a':1234,'b':0})

if __name__=='__main__': unittest.main()
