import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import uuid
#from utilities import *
import math

# convert degrees to disc type
# Boundaries for disc type
CIRCLE = list(range(361))

BOUNDARIES = {
    'IS': CIRCLE[350:] + CIRCLE[:12],
    'Is': CIRCLE[12:35],
    'I': CIRCLE[35:57],
    'Id': CIRCLE[57:80],
    'DI': CIRCLE[80:102],
    'Di': CIRCLE[102:125],
    'D': CIRCLE[125:147],
    'Dc': CIRCLE[147:170],
    'CD': CIRCLE[170:192],
    'Cd': CIRCLE[192:215],
    'C': CIRCLE[215:237],
    'Cs': CIRCLE[237:260],
    'SC': CIRCLE[260:282],
    'Sc': CIRCLE[282:305],
    'S': CIRCLE[305:327],
    'Si': CIRCLE[327:350],
}

def degrees_to_disc_type(degrees):
    try:
        degrees = float(degrees)
        # Ensure BOUNDARIES is defined
        if 'BOUNDARIES' not in globals():
            return "disc type not available"
        
        # Ensure BOUNDARIES is a dictionary
        if not isinstance(BOUNDARIES, dict):
            return "disc type not available"
        
        # Check for valid input
        if not isinstance(degrees, (int, float)):
            return "disc type not available"
        
        for disc_type, boundary in BOUNDARIES.items():
            if degrees in boundary:
                return disc_type
        
        # handle nan
        if math.isnan(degrees):
            return "disc type not available"

        # If the function hasn't returned by now, the disc type is not available
        return "disc type not available"
    
    except Exception:
        return "disc type not available"
    



# read in excel file
@st.cache_data
def load_data_wa():
    #path = "/Users/bramtunggala/CrystalKnows/ml-models/local/github/contentDashboard/data/"
    path = "./data/sample_sugggestion.xlsx"
    #path ="/Users/bramtunggala/CrystalKnows/ml-models/local/github/crystal-app/data/Crystal DISC Email Suggestion Model.xlsx"
    wa_df = pd.read_excel(path, engine='openpyxl')
    # add DISC type column
    wa_df["DiSC Type"] = wa_df["degrees"].apply(lambda x: degrees_to_disc_type(x))
    
    return wa_df # return first 15 rows




# Display Statistics
def display_statistics(wa_df):
    st.write("## Data Overview")

    # Create columns for KPIs
    col1, col2 = st.columns([2,1,])

    # Display KPIs in columns with styling
    with col1:
        st.subheader("Number of Rows")
        formatted_total_profiles = f"{len(wa_df):,}" 
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: green;'>{formatted_total_profiles}</div>", unsafe_allow_html=True)
        #st.markdown(f"**{total_profiles}**", unsafe_allow_html=True)

    with col2:
        st.subheader("Number of Categories")
        formatted_monthly_avg = f"{wa_df.category.nunique():,.0f}"
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: blue;'>{formatted_monthly_avg}</div>", unsafe_allow_html=True)
        #st.markdown(f"**{formatted_monthly_avg}**", unsafe_allow_html=True)





def view_data(wa_df):
    # st.write("Search content - Type in a value to search")
    column_name = st.selectbox("Choose a column to search from", ['search_term', 'replacement', 'DiSC Type'])

    unique_values = wa_df[column_name].unique()
    selected_value = st.selectbox(f"Search content (you can type it in too) --> column: {column_name}", unique_values)

    selected_data = wa_df[wa_df[column_name] == selected_value]
    
    # If "tags" is selected, display data with st.table to allow row selection
    if column_name == 'DiSC Type':
        # add data metrics
        st.write("Number of Rows")
        st.markdown(f"<div style='font-size: 30px; text-align: left; color: blue;'>{len(selected_data)}</div>", unsafe_allow_html=True)
        st.write("Data Selected")
        st.dataframe(selected_data)
       
    else:  
        # For "text", "search_term", "replacement", "disc type", and other columns
        st.write("Data Selected")
        st.dataframe(selected_data)
        
        # Display the first row's index from the filtered data if there's at least one row in the result
        if not selected_data.empty:
            row_index = selected_data.index.values[0]
            st.write("**Row Index:**")
            st.markdown(f"<div style='font-size: 30px; text-align: left; color: green;'>{row_index}</div>", unsafe_allow_html=True)
        else:
            st.write("No data found for the selected value.")


# function to edit 'text' column
def edit_content(action, tone, replacement):
    if action == 'replace':
    # pattern for f
        suggestion = f"""To be <b>{tone}</b>, replace [original] with [y]{replacement}[/y]"""

    elif action == 'remove':
        suggestion = f"""Remove this to be more <b>{tone}</b>"""

    else:
        suggestion = f"""Not Found"""

    return suggestion


def edit_selected_row(wa_df):
    row_index = st.number_input("Enter the row index to edit (0-indexed)", value=0, min_value=0, max_value=len(wa_df)-1)
    selected_row = wa_df.iloc[row_index]
    # show selected row
    st.write("Selected Row")
    cols = ['text', 'degrees', 'DiSC Type', 'search_term', 'category', 'action', 'tone',
       'replacement'] # select certain rows only
    st.dataframe(selected_row[cols], use_container_width=True) 

    st.divider()
    st.write("### Edit Content *here*")
    # List of columns that can be edited
    editable_columns = ['search_term', 'replacement'] 

    # Use a dictionary to hold editable values
    editable_values = {col: st.text_input(f"Edit {col}", value=str(selected_row[col])) for col in editable_columns}
    
    if st.button("Update Row"):
        # Update the dataframe with the edited values
        for col, new_value in editable_values.items():
            wa_df.at[row_index, col] = new_value
        
        action = wa_df.at[row_index, 'action']
        tone = wa_df.at[row_index, 'tone']
        replacement = wa_df.at[row_index, 'replacement']

        # update 'text' column
        wa_df.at[row_index, 'text'] = edit_content(action, tone, replacement)
        
        # handle error
        if 'updated_at' not in wa_df.columns:
            wa_df['updated_at'] = None  # Creates a new column
        wa_df['updated_at'] = wa_df['updated_at'].astype('object')

        # update "updated_at" time stamp
        wa_df.at[row_index, 'updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.success(f"Row {row_index} updated successfully!")
        # display updated row
        st.write("Updated Row")
        st.dataframe(wa_df.iloc[row_index][cols], use_container_width=True)

    return wa_df

# add a add row function
def add_new_row(wa_df):
    st.write("## Add a New Row")

    # Create input fields for each column
    search_term = st.text_input("Enter search term")
    replacement = st.text_input("Enter New Suggestion or *replacement*")
    degree = st.text_input("Enter degrees - *Must be (0-360)*")
    DiSC_Type = degrees_to_disc_type(degree)
    tone = st.text_input("Enter tone")
    category = st.text_input("Enter category")
    action = st.selectbox("Select action - *replace* or *remove*", ['replace', 'remove'])
    
    if st.button("Add Row"):
        # Append new data to the dataframe
        new_data = pd.DataFrame({
            'text': edit_content(action, tone, replacement),
            'degrees': degree,
            'DiSC Type': DiSC_Type,
            'search_term': search_term,
            'category': category,
            'tone':tone,
            'action':action,
            'replacement': replacement,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # add more columns if needed
        }, index=[0])
        wa_df = pd.concat([wa_df,new_data], ignore_index=True)
        st.success("Row added successfully!")
        st.write("added row:")
        st.write(wa_df.tail(1))
    
    return wa_df

### ------------------ ###
# delete row
def delete_row(wa_df):
    st.write("## Delete a Row")

    # Select the index of the row to delete
    row_to_delete = st.number_input("Enter the index of the row you want to delete", 
                                    min_value=0, 
                                    max_value=len(wa_df) - 1, 
                                    value=0, 
                                    format="%d")
    # show the row to delete
    st.write("Are you sure you want to **Delete** 👇this row?")
    selected_row = wa_df.iloc[row_to_delete].T
    cols = ['text', 'degrees', 'DiSC Type', 'search_term', 'category', 'action', 'tone',
       'replacement'] # select certain rows only
    st.dataframe(selected_row[cols], use_container_width=True) 

    if st.button("Delete Row!", type="primary"):
        if row_to_delete in wa_df.index:
            wa_df.drop(row_to_delete, inplace=True)
            wa_df.reset_index(drop=True, inplace=True)
            st.success(f"Row {row_to_delete} deleted successfully!")
        else:
            st.warning(f"Row {row_to_delete} not found!")
    
    return wa_df

### ------------------ ###
# function to save edited data
def save_excel(wa_df):
    if st.button("Save Content",type="primary"):
        #path = "/Users/bramtunggala/CrystalKnows/ml-models/local/github/crystal-app/data/Crystal DISC Email Suggestion Model.xlsx"
        path = "/.data/sample_suggestions.xlsx"
        wa_df.to_excel(path, index=False, engine='openpyxl')
        st.write("Excel file saved!")





### ------------------ ###
def main():
    
    st.set_page_config(page_title="✏️ WA Manager")

    # load data 
    if "wa_df" not in st.session_state:
        st.session_state.wa_df = load_data_wa()

    st.write("# ✏️ Writing Assistant Manager")

    # display stats 
    display_statistics(st.session_state.wa_df)
    ### ------------------ ###
    st.write("## View Data")
    # if "old_wa_df" not in st.session_state:
    #     st.session_state.old_wa_df = load_data_wa()
    view_data(st.session_state.wa_df)

    ### ------------------ ###
    # edit content
    st.divider()
    st.write("## Edit Content")
    on = st.checkbox('Click to edit content')
    if on:
        st.session_state.wa_df = edit_selected_row(st.session_state.wa_df)
    
        # if edit_selected_row:
        #     #st.write(st.session_state.wa_df.head(3))
        #     st.write("Most recent Updated At: ", st.session_state.wa_df['updated_at'].max())

    # ### ------------------ ###
    # add new row
    st.divider()
    st.write("## Add New Content")
    on = st.checkbox('Click to add new content')
    if on:
        st.session_state.wa_df = add_new_row(st.session_state.wa_df)

    ### ------------------ ###
    # delete row
    st.divider()
    st.write("## Delete Content")
    on = st.checkbox('Click to delete content')
    if on:
        st.session_state.wa_df = delete_row(st.session_state.wa_df)
        
    ### ------------------ ###
    # save excel
    st.divider()
    save_excel(st.session_state.wa_df)

       

if __name__ == "__main__":
    main()
