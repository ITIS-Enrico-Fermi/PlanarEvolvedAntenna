import yaml
import re
from typing import TextIO

class Config:
  class ShapeConstraints:
    outerDiam: float
    innerDiam: float
    centerShift: float
    targetFreq: float
    groundPlaneDistanceMin: float
    groundPlaneDistanceMax: float
  
  class GeneticAlgoTuning:
    populationSize: int
    iterationsNumber: int
    cutPoints: int
    mutationRate: float
    turnoverRate: float

  class GeneEncoding:
    segmentsNumber: int
    splineInterpolation: bool
    maxAngle: float
    maxSegmentLen: float
    minSegmentLen: float

  def loadYaml(stream: TextIO):
    d = yaml.safe_load(stream)
    
    Config.ShapeConstraints.outerDiam = d["shape_constraints"]["outer_diameter"]
    Config.ShapeConstraints.innerDiam = d["shape_constraints"]["inner_diameter"]
    Config.ShapeConstraints.centerShift = d["shape_constraints"]["center_shift"]
    Config.ShapeConstraints.targetFreq = d["shape_constraints"]["target_frequency"]
    Config.ShapeConstraints.groundPlaneDistanceMin = d["shape_constraints"]["gp_distance_min"]
    Config.ShapeConstraints.groundPlaneDistanceMax = d["shape_constraints"]["gp_distance_max"]

    Config.GeneticAlgoTuning.populationSize = d["genetic_algo_tuning"]["population_size"]
    Config.GeneticAlgoTuning.iterationsNumber = d["genetic_algo_tuning"]["iterations_number"]
    Config.GeneticAlgoTuning.cutPoints = d["genetic_algo_tuning"]["cut_points"]
    Config.GeneticAlgoTuning.mutationRate = d["genetic_algo_tuning"]["mutation_rate"]
    Config.GeneticAlgoTuning.turnoverRate = d["genetic_algo_tuning"]["turnover_rate"]

    Config.GeneEncoding.segmentsNumber = d["gene_encoding"]["segments_number"]
    Config.GeneEncoding.splineInterpolation = d["gene_encoding"]["spline_interpolation"]
    Config.GeneEncoding.maxAngle = d["gene_encoding"]["max_angle"]
    Config.GeneEncoding.maxSegmentLen = d["gene_encoding"]["max_segment_length"]
    Config.GeneEncoding.minSegmentLen = d["gene_encoding"]["min_segment_length"]