import unittest
from util.yolo import *
from unittest_data_provider import data_provider

# To run tests python -m unittest util.yolo_test

class TestStringMethods(unittest.TestCase):

    def test_remove_overlapping_predictions(self):

        predictions = [
            Prediction("1", .29, 1, 1, 1, 1),
            Prediction("1", .49, 1, 1, 1, 1),
            Prediction("9", .91, 1, 1, 1, 1),
            Prediction("0", .54, 1, 1, 1, 1),
            Prediction("0", .91, 1, 1, 1, 1),
            Prediction("9", .55, 1, 1, 1, 1),
            Prediction("8", .83, 1, 1, 1, 1),
            Prediction("8", .31, 1, 1, 1, 1),
            Prediction("0", .94, 1, 1, 1, 1),
            Prediction("0", .79, 1, 1, 1, 1),
            Prediction("1", .39, 1, 1, 1, 1),
            Prediction("1", .73, 1, 1, 1, 1),
            Prediction("1", .42, 1, 1, 1, 1),
        ]

        filtered_predictions = non_maximal_supression(predictions, intersection_over_union)

        self.assertEqual(filtered_predictions, [
            Prediction("0", .94, 1, 1, 1, 1)
        ])



    iou_coefficient_data = lambda: (
        ( 
            Prediction("1", .81, 0.017213000000000003, 0.22735299999999997, 0.062394, 0.428640),
            Prediction("2", .74, 0.05788, 0.35887800000000003, 0.087644, 0.455768),
            0.10717147239853668,
        ),
        ( 
            Prediction("7", 0.453746, 0.03177200000000001, 0.08161599999999997, 0.125936, 0.420806),
            Prediction("0", .843898, 0.0628025, 0.17267949999999999, 0.130953, 0.458097),
            0.38308969867192555
        ),
        ( 
            Prediction("2", 0.435066, 0.4257425, 0.07450349999999997, 0.115223, 0.436109),
            Prediction("0", .421482, 0.45552050000000005, 0.4348995, 0.120197, 0.468461),
            0.06463603055023015,
        ),
    )

    @data_provider(iou_coefficient_data)
    def test_intersection_over_union(self, a, b, result):
        iou = intersection_over_union(a,b)
        self.assertEqual(result, iou)
        
    

    overlap_coefficient_data = lambda: (
        ( 
            Prediction("1", .81, 0.017213000000000003, 0.22735299999999997, 0.062394, 0.428640),
            Prediction("2", .74, 0.05788, 0.35887800000000003, 0.087644, 0.455768),
            0.2413730717906004,
        ),
        ( 
            Prediction("7", 0.453746, 0.03177200000000001, 0.08161599999999997, 0.125936, 0.420806),
            Prediction("0", .843898, 0.0628025, 0.17267949999999999, 0.130953, 0.458097),
            0.5905198343910082,
        ),
        ( 
            Prediction("2", 0.435066, 0.4257425, 0.07450349999999997, 0.115223, 0.436109),
            Prediction("0", .421482, 0.45552050000000005, 0.4348995, 0.120197, 0.468461),
            0.12874277945647739,
        ),
    )

    @data_provider(overlap_coefficient_data)
    def test_overlap_coefficient(self, a, b, result):
        oc = overlap_coefficient(a, b)
        self.assertEqual(result, oc)
        


    projected_overlap_coefficient_data = lambda: (
        ( 
            Prediction("1", .81, 0.017213000000000003, 0.22735299999999997, 0.062394, 0.428640),
            Prediction("2", .74, 0.05788, 0.35887800000000003, 0.087644, 0.455768),
            0.34822258550501645,
        ),
        ( 
            Prediction("7", 0.453746, 0.03177200000000001, 0.08161599999999997, 0.125936, 0.420806),
            Prediction("0", .843898, 0.0628025, 0.17267949999999999, 0.130953, 0.458097),
            0.7536010354465762,
        ),
        ( 
            Prediction("2", 0.435066, 0.4257425, 0.07450349999999997, 0.115223, 0.436109),
            Prediction("0", .421482, 0.45552050000000005, 0.4348995, 0.120197, 0.468461),
            0.7415620145283488,
        ),
    )

    @data_provider(projected_overlap_coefficient_data)
    def test_projected_overlap_coefficient(self, a, b, result):
        poc = projected_overlap_coefficient(a,b)
        self.assertEqual(result, poc)


if __name__ == '__main__':
    unittest.main()