# Book Club

As part of my full-stack software development diploma, I have created an application utilising database storage. The focus has been on the back-end programming, allowing users to store and manipulate data via the frontend.  
 
This is a book review app on which users can create an account, add books, review books and save a list of books they have read and that they want to read. 

# Contents

- User Experience
    - Strategy
    - User Stories
    - Design
    - Features
- Technologies
    - Languages
    - Libraries, Frameworks and programs
- Testing
- Bugs and Fixes
- Deployment
- Credits

# User Experience

## Strategy
---
### User goals
- Review books they have read
- Find their next book based off description and reviews

### Site owner goals
- Have an intuitive site
- Have the site look clean and unmuddled
- Build a media presence to increase the nember of user to increase the range of books and reviews.

## User Stories
---  
### First time users
1. As a user I want to know what the app is for
2.  As a user I want to be able to make an account
    
### Registired Users
3. As a registired user I want to be able to write reviews
4. As a registired user I want to be able to edit my reviews
5. As a registired user I want to be able to delete my reviews
6. As a registired user I want to be able to Add books
7. As a registired user I want to be able to vote books up or down

## Design
---
### Color scheme and imagery

At first I simply wantd a clean and light design, but as it developed I wanted it to feel remenicent of a classic study, or warm cluttered library; Deep browns and green, with imagry of books. The layout was to be functional and professional, whilst still maintaining a warm and cosy feel. 


![Stacks of books](docs/README-imgs/large-selection-of-books.jpg)
![Cosy Library](docs/README-imgs/cosy-library.jpg)
![Writing desk](docs/README-imgs/classic-writing-desk.jpg)
![Classic study](docs/README-imgs/classic-study.jpg)


### Typography

Fitting with the 'classic' astetic, I chose two main fonts: 
- ![Italianno](docs/README-imgs/font-italianno.png)
- ![Martel600](docs/README-imgs/font-martel.png)


### wireframes

Althought the final product differs from these first designs, the layout and pages are mostly the same.
[link to wireframs](docs/README-imgs/wireframes)

## Features
---  
####Nav bar

All pages have the same nav bar located at the top of the screen.
    
    - The 'Book Club' link is located at the top left, this takes the user to the home page.
    
    If the user is not logged in:

    - A 'log in' link is located at top right. This takes the user to a log in page.

    - A 'sign up' link is located at the top right. This takes the user to a sign up page.

    If the user is logged in:

    - A 'Search Books' link is located at the rop right. This takes the user to the home page.

    - A 'My Library' link is located at the top right. This takes the user to a page where they can view books they have saved.

    - A 'My Reviews' link is located at the top right. This takes the user to a page where they can view the reviews they have left.

    - A 'My Profile' link is located at the top right. This takes the user to a page where they can access their books, reviews as well as links to add books and edit their account details.

    - A 'Log out' link is located at the top right. This logs the user out and takes them to the log in page.

On screens with a max-width of 600px, the 'Book Club' link is top center and there is a drop down nav bar located at the top left of the screen with all the same links as the larger screens.

#### Home page

This is where the user can search all the books in the database.

    If the user is not logged in:

    - There is a flashing call to action in the center of the screen which takes the user to the sign up page.

    - Below the CTA there is a search bar which takes an input.

    - A 'Reset' button sits below the search bar and reloads the home page, clearing any searches.

    - A 'Search' button sits below the search bar and reloads the home page with books based on the search input.

    

### future features

# Technologies

## Languages
---
- HTML5
- CSS3
- Python

## Libraries, Frameworks and programs
---
- GitHub
- GitPod
- FontAwesome
- Materialise
- Flask
- MongoDB
- Werkzeug
- Heruko
- JQuery
- AmIResponsive
- RandomKeyGen
- Jinja

# Testing
# Bugs and Fixes
# Deployment
# Credits
- stars - https://bennettfeely.com/
- star rating - BananaCoding https://www.youtube.com/watch?v=8qCJahxZ9nQ