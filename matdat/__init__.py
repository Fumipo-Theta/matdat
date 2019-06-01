from .figure import Figure
from .subplot import Subplot
from .subplot_time import SubplotTime
from .csv_reader import CsvReader, matchCsv
from .excel_reader import ExcelReader
from .get_path import getFileList, PathList, multiple_path_finder
from .save_plot import actionSavePNG


print("""MatDat is deprecated.
Please migrate into 'structured_plot' and 'data_loader' package
""")
