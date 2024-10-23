from PIL import Image
import io

def display_graph(graph):
  try:
      # Get the PNG data as bytes
      png_data = graph.get_graph().draw_mermaid_png()
      
      # Save the PNG data to a file
      with open("mermaid_diagram.png", "wb") as f:
          f.write(png_data)
      
      print("Mermaid diagram saved as 'mermaid_diagram.png'")
      
      # Open and display the image using PIL
      img = Image.open(io.BytesIO(png_data))
      img.show()
      
      print("The image should now open in your default image viewer.")
  except Exception as e:
      print(f"Error saving or displaying the diagram: {e}")