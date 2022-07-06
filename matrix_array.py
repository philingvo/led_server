def get_matrix_array(matrix_setting):
    
    def changeArray(led_array, connection_angle_x):
    
        def transMatrix(input_matrix):
            columns = len(input_matrix)
            rows = len(input_matrix[0])
            output_matrix = []
            for row in range(rows):
                new_row = []
                for column in range(columns):
                    new_row.append(input_matrix[column][row])
                output_matrix.append(new_row)
            return output_matrix
          
        def reverse_columns(led_array, connection_angle_x):
            rest = 0 if connection_angle_x else 1
            for row_number in range(len(led_array)):
                if row_number % 2 == rest:
                    new_row = []
                    for column_number in range(len(led_array[row_number])-1, -1, -1):
                        new_row.append(led_array[row_number][column_number])
                    led_array[row_number] = new_row
        
        reverse_columns(led_array, connection_angle_x)
        return transMatrix(led_array)
    
    width = matrix_setting.width
    height = matrix_setting.height
    direction = matrix_setting.direction
    connection_angle_x = matrix_setting.connection_angle_x
    connection_angle_y = matrix_setting.connection_angle_y
    
    if connection_angle_x:
        start_x, finish_x, increment_x = width-1, -1, -1
    else:
        start_x, finish_x, increment_x = 0, width, 1
    
    if connection_angle_y:
        start_y, finish_y, increment_y = height-1, -1, -1
    else:    
        start_y, finish_y, increment_y = 0, height, 1
    
    if direction:
        start_x, finish_x, increment_x, start_y, finish_y, increment_y = start_y, finish_y, increment_y, start_x, finish_x, increment_x
        rows, columns = width, height        
    else:
        rows, columns = height, width
    
    led_array = [y for y in range(rows)]
    for y in range(start_y, finish_y, increment_y):    
        led_array[y] = [x for x in range(start_x, finish_x, increment_x)]
        start_x += columns
        finish_x += columns
    
    if direction:        
        led_array = changeArray(led_array, connection_angle_x)
    
    return led_array