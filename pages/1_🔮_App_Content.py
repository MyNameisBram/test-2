# this is a github version
import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import uuid



# read in excel file
@st.cache_data
def load_data():
    #path = "/Users/bramtunggala/CrystalKnows/ml-models/local/github/contentDashboard/data/"
    #path = "./data/"
    path = "/Users/bramtunggala/CrystalKnows/ml-models/local/github/crystal-app/data/"
    file_name = "Personality Datums.xlsx"
    df = pd.read_excel(path+file_name, engine='openpyxl')
    # rename column
    df.rename(columns={'Unnamed: 0': 'uuid', 'Unnamed: 8' :'updated_at'}, inplace=True)
    # convert date column to datetime
    df['updated_at'] = pd.to_datetime(df['updated_at'])
   
    return df 


# view data to search/select
def view_data(df):
    #col =['text']
    #st.write("Search content - Type in a value to search")
    column_name = st.selectbox("Choose a column to search from", ['text', 'tags'])

    unique_values = df[column_name].unique()
    selected_value = st.selectbox(f"Search content (you can type it in too) --> column: {column_name}", unique_values)
    # data_edit
    selected_data = df[df[column_name] == selected_value]
    
    #If "tags" is selected, display data with st.table to allow row selection
    if column_name == 'tags':
        # add data metrics
        st.write("Number of Rows")
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: blue;'>{len(selected_data)}</div>", unsafe_allow_html=True)
        st.write("Data Selected")
        st.dataframe(selected_data)
       
    else:
        # For "text" just use st.dataframe and display the first row's index from the filtered data
        st.write("Data Selected")
        st.dataframe(selected_data)
        row_index = selected_data.index.values[0]
        st.write("**Row Index:**")
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: green;'>{row_index}</div>", unsafe_allow_html=True)




# Display Statistics
def display_statistics(df):
    st.write("## Data Overview")

    # Create columns for KPIs
    col1, col2 = st.columns([2,1,])

    # Display KPIs in columns with styling
    with col1:
        st.subheader("Number of Rows")
        formatted_total_profiles = f"{len(df):,}" 
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: green;'>{formatted_total_profiles}</div>", unsafe_allow_html=True)
        #st.markdown(f"**{total_profiles}**", unsafe_allow_html=True)

    with col2:
        st.subheader("Number of Tags")
        formatted_monthly_avg = f"{df.tags.nunique():,.0f}"
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: blue;'>{formatted_monthly_avg}</div>", unsafe_allow_html=True)
        #st.markdown(f"**{formatted_monthly_avg}**", unsafe_allow_html=True)



# function to save edited data
def save_excel(df):
    if st.button("Save Content",type="primary"):
        path = "./data/"
        path = "/Users/bramtunggala/CrystalKnows/ml-models/local/github/crystal-app/data/"
        file_name = "Personality Datums.xlsx"
        df.to_excel(path+file_name, index=False, engine='openpyxl')
        st.write("Excel file saved!")
  

def edit_selected_row(df):
    row_index = st.number_input("Enter the row index to edit (0-indexed)", value=0, min_value=0, max_value=len(df)-1)
    selected_row = df.iloc[row_index]

    # List of columns that can be edited
    editable_columns = ['text', 'tags', 'degrees', 'intensity', 'degrees_2', 'intensity_2'] 

    # Use a dictionary to hold editable values
    editable_values = {col: st.text_input(f"Edit {col}", value=str(selected_row[col])) for col in editable_columns}
    
    if st.button("Update Row"):
        # Update the dataframe with the edited values
        for col, new_value in editable_values.items():
            df.at[row_index, col] = new_value
        # add time stamp
        df.at[row_index, 'updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.success(f"Row {row_index} updated successfully!")

    return df

# add a add row function
def add_new_row(df):
    st.write("## Add a New Row")

    # Create input fields for each column
    new_text = st.text_input("Enter text")
    new_tags = st.text_input("Enter tags")
    new_degrees = st.text_input("Enter degrees")
    new_intensity = st.text_input("Enter intensity")
    new_degrees_2 = st.text_input("Enter degrees_2")
    new_intensity_2 = st.text_input("Enter intensity_2")
    
    if st.button("Add Row"):
        # Append new data to the dataframe
        new_data = pd.DataFrame({
            'uuid': uuid.uuid4(),
            'text': new_text,
            'tags': new_tags,
            'degrees': new_degrees,
            'intensity': new_intensity,
            'degrees_2': new_degrees_2,
            'intensity_2': new_intensity_2,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # add more columns if needed
        }, index=[0])
        df = pd.concat([df,new_data], ignore_index=True)
        st.success("Row added successfully!")
        st.write("added row:")
        st.write(df.tail(1))
    
    return df

### ------------------ ###
# delete row
def delete_row(df):
    st.write("## Delete a Row")

    # Select the index of the row to delete
    row_to_delete = st.number_input("Enter the index of the row you want to delete", 
                                    min_value=0, 
                                    max_value=len(df) - 1, 
                                    value=0, 
                                    format="%d")
    
    # show the row to delete
    st.write("Are you sure you want to **Delete** 👇this row?")
    selected_row = df.iloc[row_to_delete].T
    #cols = ['text', 'degrees', 'DiSC Type', 'search_term', 'category', 'action', 'tone',
       #'replacement'] # select certain rows only
    st.dataframe(selected_row, use_container_width=True) 

    if st.button("Delete Row!", type="primary"):
        if row_to_delete in df.index:
            df.drop(row_to_delete, inplace=True)
            df.reset_index(drop=True, inplace=True)
            st.success(f"Row {row_to_delete} deleted successfully!")
        else:
            st.warning(f"Row {row_to_delete} not found!")
    
    return df





### ------------------ ###
def main():
    st.set_page_config(page_title="App Content", page_icon="🔮")
    # load data 
    if "df" not in st.session_state:
        st.session_state.df = load_data()

    st.write("# Crystal Content Manager 🔮")

    # display stats 
    display_statistics(st.session_state.df)
    ### ------------------ ###
    st.write("## View Data")
    # unhash this if you want to view old data
    # if "old_df" not in st.session_state:
    #     st.session_state.old_df = load_data()
    # view current data
    view_data(st.session_state.df)

    ### ------------------ ###
    # edit content
    st.divider()
    st.write("## Edit Content")
    on = st.checkbox('Click to edit content')
    if on:
        st.session_state.df = edit_selected_row(st.session_state.df)
    
        if edit_selected_row:
        
            #st.write(st.session_state.df.head(3))
            st.write("Most recent Updated At: ", st.session_state.df['updated_at'].max())

    ### ------------------ ###
    # add new row
    st.divider()
    st.write("## Add New Content")
    on = st.checkbox('Click to add new content')
    if on:
        st.session_state.df = add_new_row(st.session_state.df)

    ### ------------------ ###
    # delete row
    st.divider()
    st.write("## Delete Content")
    on = st.checkbox('Click to delete content')
    if on:
        st.session_state.df = delete_row(st.session_state.df)
        
    ### ------------------ ###
    # save excel
    st.divider()
    save_excel(st.session_state.df)

       

if __name__ == "__main__":
    main()


