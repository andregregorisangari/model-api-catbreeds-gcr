import os
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from PIL import Image

app = Flask(__name__)
app.config["ALLOWED_EXTENSIONS"] = set(['png', 'jpg', 'jpeg'])
app.config["UPLOAD_FOLDER"] = "static/uploads/"

def allowed_file(filename):
    return "." in filename and \
        filename.split(".", 1)[1] in app.config["ALLOWED_EXTENSIONS"]

model = load_model("EfficientNet_model2.h5", compile=False)
with open("labels.txt", "r") as file:
    labels = file.read().splitlines()

# Tambahkan kamus deskripsi kucing
cat_descriptions = {
    'Abyssinian': "THIS SLINKY, GRACEFUL CAT IS FULL OF ENERGY AND NEEDS SPACE TO PLAY AND EXPLORE. There are various accounts of the Abyssinian’s history, including the attractive but highly improbable story that it descends from the sacred cats of Ancient Egypt. With its athletic build, aristocratic bearing, and beautiful ticked coat, the Abyssinian is a striking cat with a hint of wild about it. Intelligent and affectionate, Abyssinians make wonderful companions but they like an all-action life.",

    'American Bobtail': "BIG AND BEAUTIFUL, THIS CAT IS AN EXCELLENT AND HIGHLY ADAPTABLE COMPANION. The breeding of domestic bobtail cats native to the US has been reported several times since about the middle of the 20th century, but so far only this one has been fully recognized. This cat is happy to be among people, without overwhelming them with its attention, and ﬁts in comfortably with any type of household. ",

    'American Shorthair': "A ROBUST, EASY-CARE CAT THAT IS RECOGNIZED IN A HUGE RANGE OF COLORS. The ﬁrst domestic cats in the US, are said to have arrived with the early pilgrims in the 1600s. Careful breeding further improved the Domestic, and by the 1960s—now renamed the American Shorthair—it was attracting attention at pedigree cat shows. Healthy and hardy, American Shorthairs are perfect family cats that ﬁt in with almost any type of household.",

    'Bengal': "THIS CAT HAS A STRIKINGLY BEAUTIFUL SPOTTED COAT AND A VIBRANT PERSONALITY. In the 1970s, scientists crossed the small, wild Asian leopard cat with short haired domestic cats in an attempt to introduce the wild cat’s natural immunity to feline leukemia into the pet population. Despite its wild ancestry, there is nothing unsafe about the Bengal—it is delightfully affectionate—but it does have a lot of energy and is best suited to an experienced cat owner. Friendly by nature, a Bengal always wants to be at the heart of its family and needs company and both physical activity and mental stimulation. A bored Bengal will be unhappy and possibly destructive.",
    
    'Birman': "THIS CAT IS QUIET AND GENTLE BUT HIGHLY RESPONSIVE TO AN OWNER’S ATTENTION. With its distinctive colorpoints, this exquisite cat has the appearance of a longhaired Siamese, but the two breeds are unlikely to be closely related. Gentle and sweet, the Birman is an exceptionally easy pet to live with. Even the long coat is not difficult to groom, since there is little undercoat to become tangled or clogged with loose hair.",

    'Bombay': "THIS PINT-SIZED “BLACK PANTHER” HAS GLOSSY FUR AND COPPERY EYES. Created speciﬁcally for its appearance, The Bombay is a cross between the American Burmese and the American Shorthair. Round and shiny, this breed comes only in black. It may look like a panther but it is a true homebody, and few cats are more loving and sociable.",

    'British Shorthair': "A CAT THAT COMBINES GOOD LOOKS WITH AN EASYGOING TEMPERAMENT. Originally developed from the best examples of ordinary British domestic cats, the British Shorthair was one of the ﬁrst pedigree cats to appear in shows during the late 19th century. Quietly affectionate, the Shorthair likes to stay near its owner. British Shorthairs generally have robust health and can be long-lived.",
    
    'Egyptian Mau': "STRIKINGLY PATTERNED, THIS IS THE ONLY NATURALLY SPOTTED DOMESTIC BREED. This cat bears a certain resemblance to the long-bodied, spotted cats seen in the tomb paintings of Ancient Egyptian pharaohs, but it cannot claim direct descent. Maus are affectionate cats but are also inclined to be sensitive and shy. They need thoughtful socializing at an early age and are probably best suited to an experienced cat owner. However, once a Mau bonds with its family, it stays devoted for life.",
    
    'Maine Coon': "AN IMPRESSIVELY LARGE CAT THAT IS KIND-NATURED AND EASY TO KEEP. Regarded as America’s native cat, the Maine Coon is named after the state where it was ﬁrst recognized. How the breed ﬁrst arrived there has been explained in various entertaining but mostly improbable tales. Maine Coons have many endearing characteristics, including a tendency to act like kittens all their lives. Their voice, described by some as a bird like chirp, sounds surprisingly small for such a big cat. These cats are slow to mature and do not usually reach their full magniﬁcent growth until about their ﬁfth year.",
    
    'Persian': "THIS CHARMING CAT IS THE ORIGINAL VERSION OF THE WORLD’S FAVORITE LONGHAIR. By the end of the 19th century, when pedigree cat shows were starting to attract worldwide interest, the Persian (sometimes referred to as the Longhair) was already very popular in the US and the UK. Persians are renowned for their gentle, affectionate temperament and home-loving personality. These are deﬁnitely not action cats, although they can be charmingly playful if offered a toy.",
    
    'Ragdoll': "THIS HUGE CAT IS REMARKABLY SWEET AND AMENABLE. The name is well chosen, because few cats are easier to handleor more ready to sit on a lap than a Ragdoll. These cats love human company, will happily play with children, and are usually well disposed toward other pets. Ragdolls are not particularly athletic and, once past kittenhood, mostly prefer their games to be gentle. Moderate grooming is enough to keep their soft, silky fur free from tangles.",
    
    'Russian Blue': "FRIENDLY BUT SELF-SUFFICIENT, THIS GRACEFUL CAT DOES NOT DEMAND MUCH ATTENTION. The most widely accepted version of this breed’s ancestry suggests that it originated around the Russian port of Archangel, just below the Arctic Circle. Supposedly brought to Europe bysailors, the Russian Blue was attracting interest in the UK well before the end of the 19th century, and had also appeared in North America by the early 20th century. Reserved with strangers, this cat has an abundance of quiet affection to give its owners. Differently colored types of the breed have been developed under the name Russian Shorthair.",
    
    'Siamese': "THIS INSTANTLY RECOGNIZABLE BREED IS UNIQUE IN LOOKS AND PERSONALITY. The history of the Siameseincludes more myths and legends than hard facts, and the true tale of this Royal Cat of Siam is now lost in time. With a super-sized ego and a loud voice that it uses to demand attention, the Siamese is the most extroverted of all cats. This highly intelligent breed is full of fun and energy and makes a wonderful family pet, as ready to give affection as to receive it.",
   
    'Sphynx': "THIS HAIRLESS CAT HAS AN ENDEARINGLY IMPISH CHARACTER. Probably the best known of the hairless cats that have appeared around the world, the Sphynx originated in Canada and was named for its supposed resemblance to the Ancient Egyptian sculpture of the mythical Sphinx. It is easy to live with but needs to be kept indoors and protected from temperature extremes. Lack of a normal coat also means that excess body oils cannot be absorbed, so regular washing is required. Cats used to baths from an early age are unlikely to object.",
   
    'Tuxedo': "WITH ITS DISTINCTIVE BLACK AND WHITE COAT, EXUDES CHARM AND ELEGANCE. Originating from various cat breeds, the Tuxedo cat is characterized by its distinctive black and white coat resembling formal wear. Their striking appearance has earned them the name 'Tuxedo.' These cats can be found in various patterns, showcasing a blend of sophistication and playfulness. The Tuxedo cat, a delightful companion, adds a touch of class to any home."
}


@app.route('/')
def index():
    return jsonify({
        "status" : {
            "code" : 200,
            "message" : "Succes fetching the API",
        },
        "data" : None,
    }),200

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    if request.method == "POST":
        image = request.files["image"]
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # Augmentasi image
            img = tf.keras.preprocessing.image.load_img(image_path)
            img_arr = tf.keras.utils.img_to_array(img)
            img_arr = img_arr / 255.
            img_arr = tf.image.resize(img_arr, [224, 224])
            img_arr = np.expand_dims(img_arr, axis=0)
            
            # Prediksi dari model
            predictions = model.predict(img_arr)
            # Label prediksi
            predicted_label = labels[np.argmax(predictions)]
            # Confidence score
            confidence_score = float(predictions[0][np.argmax(predictions)])
            # Ambil nama ras kucing  dari label prediksi
            cat_breed_name = predicted_label
            # Dapatkan deskripsi dari kamus
            cat_breed_description = cat_descriptions.get(cat_breed_name)



            return jsonify({
                "status": {
                    "code": 200,
                    "photo": request.host_url + image_path,
                    "message": "Success Predict!",
                },
                "data": {
                    "Cat_breed_Predictions": cat_breed_name,
                    "Cat_breed_Description": cat_breed_description,
                    "confidence": confidence_score
                }
            }),200
        else:
            return jsonify({
                "status" : {
                    "code" : 400,
                    "message" : "Bad request",
                },
                "data" : None,
            }),400
    else:
        return jsonify({
            "status" : {
                "code" : 405,
                "message" : "Method not allowed",
            },
            "data" : None,
        }),405


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))