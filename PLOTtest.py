from DATAclass import DATAclass

local_folder = f"Ensaios"

test_name = "MOS8_OUTPUT"

data = DATAclass()
data.plot_output_characteristic(local_folder, test_name, x_axis='Vds')
