function deleteVenue(venueId){
	fetch('/venues/'+venueId, {
		method: 'DELETE'
	})
	.then(function(response){
		return response.json();
	})
	.then(function(jsonResponse){
		if(jsonResponse['success']){
			alert('Succesfully deleted venue with id '+venueId);
			window.location.replace('/');
		} else{
			alert('Error deleting venue with id '+venueId);
		}
	})
	.catch(function(err){
		console.log('create todo error ', err.message);
	})
}