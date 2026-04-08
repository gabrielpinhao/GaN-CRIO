from DATAclass import DATAclass

local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

test_name = "MOS7_OUTPUT"

data = DATAclass()
data.plot_output_characteristic(local_folder, test_name)
