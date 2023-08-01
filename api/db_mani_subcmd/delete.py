
import callDjango
callDjango.DjangoAPIBase().call_django()
from PPBWidgets import models

def main():
    all_species = models.Species.objects.all()
    print("id\tspecies_name")
    for i in all_species:
        print(i.id,"\t",i.species_name)
    print("Input id to delete (q to quit)")
    input_id = input()
    if input_id == 'q':
        print("Goodbye!")
        return -1
    else:
        models.Species.objects.get(id=input_id).delete()

if __name__ == '__main__':
    main()