import streamlit as st
import math
import base64
from PIL import Image
from io import BytesIO
from algorithm import allocate


def main():
    image_path = 'drivepairlogo.png'
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    html_code = f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{img_base64}" width="130" style="display: block; margin: 0 auto;" />
            </div>
        """
    st.markdown(html_code, unsafe_allow_html=True)

    cars_list = [
        "Perodua Axia",
        "Proton Saga",
        "Perodua Myvi",
        "Perodua Bezza",
        "Proton Iriz",
        "Toyota Vios",
        "Proton X50",
        "Perodua Ativa",
        "Proton Persona",
        "Honda City",
        "Honda WRV",
        "Toyota Yaris",
        "Ford Fusion",
        "Chevrolet Malibu",
        "Hyundai Sonata",
        "Nissan Altima",
        "Volkswagen Passat",
        "Subaru Legacy",
        "Mazda 6",
        "Kia Optima"
    ]
    st.title("DrivePair")
    st.header("Less Cars, More Share, More Care.")
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("1) For safety purposes, each car needs to have at least 2 passengers with driving license.")
    st.write("2) This system is designed to use the fewest cars possible based on the number of passengers to save fuel.")
    st.write("3) Each passenger must select at least one of the available cars that they would like to travel with.")
    st.write("4) The maximum people onboard for each car is 5")
    st.markdown("<br>", unsafe_allow_html=True)
    # Determine the number of passengers and cars
    no_passengers = st.number_input("Enter the number of passengers", min_value=2, max_value=100, value=7, step=1)
    st.markdown("<br>", unsafe_allow_html=True)
    no_cars = math.ceil(no_passengers/5)
    st.write(f"**Based on the number of passengers, the number of cars to choose from is {no_cars}.**")
    st.markdown("<br>", unsafe_allow_html=True)


    # Collect names and preferences
    passenger_data = {}
    license_indices = []
    for i in range(no_passengers):
        with st.expander(f"Passenger {i+1} details"):
            name = st.text_input(f"Name for passenger {i+1}", key=f"name_{i}")
            if name:  # Ensure a name has been entered to save preferences
                passenger_data[name] = []
                for j in range(no_cars):
                    if st.checkbox(f"{cars_list[j]}", key=f"pref_{i}_{j}"):
                        passenger_data[name].append(j)
                if st.checkbox("Has driving license?", key=f"license_{i}"):
                    license_indices.append(i)

    passenger_in = []

    for passenger in passenger_data:
        passenger_in.append(passenger_data[passenger])

    # Button to perform allocation
    if st.button("Allocate"):
        if passenger_data and license_indices:
            print(passenger_in)
            print(license_indices)
            allocation_result = allocate(passenger_in, license_indices)
            print(allocation_result)
            if allocation_result is None:
                st.error("No valid car allocation possible.")
            else:
                st.success("Car allocation result:")
                passenger_names = list(passenger_data.keys())
                for i in range(len(allocation_result)):
                    st.subheader(f"{cars_list[i]}")
                    for j in range(len(allocation_result[i])):
                        st.write(f"{j+1}) {passenger_names[allocation_result[i][j]]}")
        else:
            st.error("Please enter valid preferences and licenses.")

if __name__ == "__main__":
    main()